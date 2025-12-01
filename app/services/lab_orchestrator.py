"""
Lab Orchestration Service
Manages Docker containers for per-user lab instances
"""
import docker
import os
import random
import string
from datetime import datetime, timedelta
from flask import current_app

# Lab image mappings
LAB_IMAGES = {
    'xss-reflected-basic': {
        'image': 'webnox-xss-reflected',
        'build_path': 'labs/xss-reflected',
        'flag': 'FLAG{xss_r3fl3ct3d_b4s1c}',
        'internal_port': 80
    },
    'xss-stored-comments': {
        'image': 'webnox-xss-stored',
        'build_path': 'labs/xss-stored',
        'flag': 'FLAG{st0r3d_xss_p3rs1st3nt}',
        'internal_port': 80
    },
    'sqli-login-bypass': {
        'image': 'webnox-sqli-login',
        'build_path': 'labs/sqli-login',
        'flag': 'FLAG{sql1_l0g1n_byp4ss}',
        'internal_port': 80
    },
    'idor-profile': {
        'image': 'webnox-idor-profile',
        'build_path': 'labs/idor-profile',
        'flag': 'FLAG{1d0r_pr0f1l3_4cc3ss}',
        'internal_port': 80
    },
    'csrf-password': {
        'image': 'webnox-csrf-password',
        'build_path': 'labs/csrf-password',
        'flag': 'FLAG{csrf_p4ssw0rd_ch4ng3}',
        'internal_port': 80
    }
}

# Port range for lab instances
PORT_RANGE_START = 10000
PORT_RANGE_END = 20000

# Used ports tracking
used_ports = set()


def get_docker_client():
    """Get Docker client instance"""
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        print(f"Docker connection error: {e}")
        return None


def generate_container_name(user_id, lab_slug):
    """Generate unique container name"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"webnox-lab-{user_id}-{lab_slug[:20]}-{random_suffix}"


def get_available_port():
    """Find an available port for the lab instance"""
    global used_ports
    
    for port in range(PORT_RANGE_START, PORT_RANGE_END):
        if port not in used_ports:
            used_ports.add(port)
            return port
    
    raise Exception("No available ports")


def release_port(port):
    """Release a port back to the pool"""
    global used_ports
    used_ports.discard(port)


def get_running_instance(user_id, lab_id):
    """Get running lab instance for a user"""
    from app.models.lab_instance import LabInstance
    
    return LabInstance.query.filter_by(
        user_id=user_id,
        lab_id=lab_id,
        status='running'
    ).first()


def build_lab_image(lab_slug):
    """Build Docker image for a lab if it doesn't exist"""
    client = get_docker_client()
    if not client:
        return False, "Docker not available"
    
    lab_config = LAB_IMAGES.get(lab_slug)
    if not lab_config:
        return False, f"Unknown lab: {lab_slug}"
    
    image_name = lab_config['image']
    build_path = lab_config['build_path']
    
    try:
        # Check if image exists
        try:
            client.images.get(image_name)
            return True, "Image exists"
        except docker.errors.ImageNotFound:
            pass
        
        # Build image
        full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), build_path)
        
        if not os.path.exists(full_path):
            return False, f"Build path not found: {full_path}"
        
        print(f"Building image {image_name} from {full_path}...")
        client.images.build(path=full_path, tag=image_name, rm=True)
        print(f"Image {image_name} built successfully")
        return True, "Image built"
        
    except Exception as e:
        return False, str(e)


def start_lab_instance(user_id, lab_slug, lab_id):
    """Start a new lab instance for a user"""
    from app.models.lab_instance import LabInstance
    from app import db
    
    client = get_docker_client()
    if not client:
        return None, "Docker is not available"
    
    lab_config = LAB_IMAGES.get(lab_slug)
    if not lab_config:
        return None, f"Unknown lab configuration: {lab_slug}"
    
    # Build image if needed
    success, msg = build_lab_image(lab_slug)
    if not success and "exists" not in msg.lower():
        return None, f"Failed to build lab image: {msg}"
    
    # Check for existing running instance
    existing = LabInstance.query.filter_by(
        user_id=user_id,
        lab_id=lab_id,
        status='running'
    ).first()
    
    if existing:
        return existing, "Instance already running"
    
    try:
        # Get available port
        host_port = get_available_port()
        container_name = generate_container_name(user_id, lab_slug)
        
        # Create container
        container = client.containers.run(
            image=lab_config['image'],
            name=container_name,
            detach=True,
            ports={f"{lab_config['internal_port']}/tcp": host_port},
            environment={
                'LAB_FLAG': lab_config['flag'],
                'USER_ID': str(user_id)
            },
            labels={
                'webnox.lab': 'true',
                'webnox.user_id': str(user_id),
                'webnox.lab_id': str(lab_id),
                'webnox.lab_slug': lab_slug
            },
            mem_limit='256m',
            cpu_period=100000,
            cpu_quota=50000,  # 50% CPU limit
            network='webnox-labs',
            auto_remove=False
        )
        
        # Determine lab URL
        host = os.environ.get('LAB_HOST', 'localhost')
        lab_url = f"http://{host}:{host_port}"
        
        # Calculate expiration (2 hours)
        expires_at = datetime.utcnow() + timedelta(hours=2)
        
        # Create database record
        instance = LabInstance(
            user_id=user_id,
            lab_id=lab_id,
            container_id=container.id,
            container_name=container_name,
            port=host_port,
            status='running',
            lab_url=lab_url,
            started_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        db.session.add(instance)
        db.session.commit()
        
        return instance, "Lab started successfully"
        
    except docker.errors.ImageNotFound:
        return None, f"Lab image not found: {lab_config['image']}"
    except Exception as e:
        release_port(host_port)
        return None, str(e)


def stop_lab_instance(instance_id=None, user_id=None, lab_id=None):
    """Stop a lab instance"""
    from app.models.lab_instance import LabInstance
    from app import db
    
    client = get_docker_client()
    
    # Find instance
    if instance_id:
        instance = LabInstance.query.get(instance_id)
    elif user_id and lab_id:
        instance = LabInstance.query.filter_by(
            user_id=user_id,
            lab_id=lab_id,
            status='running'
        ).first()
    else:
        return False, "No instance specified"
    
    if not instance:
        return False, "Instance not found"
    
    try:
        if client and instance.container_id:
            try:
                container = client.containers.get(instance.container_id)
                container.stop(timeout=5)
                container.remove()
            except docker.errors.NotFound:
                pass
        
        # Release port
        release_port(instance.port)
        
        # Update database
        instance.status = 'stopped'
        instance.stopped_at = datetime.utcnow()
        db.session.commit()
        
        return True, "Lab stopped successfully"
        
    except Exception as e:
        return False, str(e)


def get_user_instances(user_id):
    """Get all lab instances for a user"""
    from app.models.lab_instance import LabInstance
    
    return LabInstance.query.filter_by(user_id=user_id).order_by(
        LabInstance.created_at.desc()
    ).all()


def get_running_instance(user_id, lab_id):
    """Get running instance for user and lab"""
    from app.models.lab_instance import LabInstance
    
    return LabInstance.query.filter_by(
        user_id=user_id,
        lab_id=lab_id,
        status='running'
    ).first()


def cleanup_expired_instances():
    """Stop all expired lab instances"""
    from app.models.lab_instance import LabInstance
    
    expired = LabInstance.query.filter(
        LabInstance.status == 'running',
        LabInstance.expires_at < datetime.utcnow()
    ).all()
    
    results = []
    for instance in expired:
        success, msg = stop_lab_instance(instance_id=instance.id)
        results.append({
            'instance_id': instance.id,
            'success': success,
            'message': msg
        })
    
    return results


def cleanup_user_instances(user_id):
    """Stop all running instances for a user"""
    from app.models.lab_instance import LabInstance
    
    instances = LabInstance.query.filter_by(
        user_id=user_id,
        status='running'
    ).all()
    
    results = []
    for instance in instances:
        success, msg = stop_lab_instance(instance_id=instance.id)
        results.append({
            'instance_id': instance.id,
            'success': success,
            'message': msg
        })
    
    return results


def get_instance_status(instance_id):
    """Get current status of a lab instance"""
    from app.models.lab_instance import LabInstance
    
    instance = LabInstance.query.get(instance_id)
    if not instance:
        return None
    
    # Check actual container status if running
    if instance.status == 'running':
        client = get_docker_client()
        if client:
            try:
                container = client.containers.get(instance.container_id)
                if container.status != 'running':
                    instance.status = 'stopped'
                    from app import db
                    db.session.commit()
            except docker.errors.NotFound:
                instance.status = 'stopped'
                from app import db
                db.session.commit()
    
    return instance
