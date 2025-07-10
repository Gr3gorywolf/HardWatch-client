import docker
import requests

from utils.network import get_host_ip, sendPing

STATUS_RUNNING = "running"
STATUS_WARNING = "warning"
STATUS_ERROR = "error"
STATUS_STOPPED = "stopped"
TIMEOUT_MS = 0.2

client = docker.from_env()



host_ip = get_host_ip()

def infer_type(name, port):
    name = name.lower()
    if port in [22]:
        return "ssh"
    if port in [3306, 5432, 27017, 6379, 1521]:
        return "database"
    if port in [21, 20, 2121]:
        return "file"
    if port in [80, 443, 8080, 8000]:
        if "dev" in name or "vite" in name or "webpack" in name:
            return "dev-server"
        elif "api" in name or "gateway" in name:
            return "code"
        return "web"
    if port in [1935, 554, 8554, 8001]:
        return "video"
    if port in [3389, 5900, 8081]:
        return "remote-control"
    if "code" in name or "api" in name:
        return "code"
    if "ssh" in name:
        return "ssh"
    if "ftp" in name or "smb" in name or "file" in name:
        return "file"
    if "rtmp" in name or "video" in name:
        return "video"
    if "vnc" in name or "remote" in name:
        return "remote-control"
    if "dev" in name:
        return "dev-server"

    return "other"

def generate_url(ip, port, type_):
    if type_ == "database":
        if port == 27017:
            return f"mongodb://{ip}:{port}"
        elif port == 5432:
            return f"postgresql://{ip}:{port}"
        elif port == 3306:
            return f"mysql://{ip}:{port}"
        elif port == 6379:
            return f"redis://{ip}:{port}"
        else:
            return f"{ip}:{port}"
    elif type_ == "web":
        return f"https://{ip}" if port == 443 else f"http://{ip}:{port}"
    elif type_ == "code" or type_ == "dev-server":
        return f"http://{ip}:{port}"
    elif type_ == "file":
        return f"ftp://{ip}:{port}" if port in [20, 21, 2121] else f"smb://{ip}:{port}"
    elif type_ == "video":
        return f"rtsp://{ip}:{port}" if port in [554, 8554] else f"http://{ip}:{port}/stream"
    elif type_ == "remote-control":
        return f"vnc://{ip}:{port}" if port == 5900 else f"rdp://{ip}:{port}"
    elif type_ == "ssh":
        return f"ssh://{ip}:{port}"
    else:
        return f"http://{ip}:{port}"
  


def get_docker_services():
    services = []
    counter = 1
    for container in client.containers.list():
        ports = container.attrs['NetworkSettings']['Ports']
        name = container.name
        for key, val in ports.items():
            if val:
                host_port = int(val[0]['HostPort'])
                service_type = infer_type(name, host_port)
                url = generate_url(host_ip, host_port, service_type)

                services.append({
                    "id": f"docker-{container.id[:12]}-{host_port}",
                    "name": name,
                    "ip": host_ip,
                    "port": host_port,
                    "type": service_type,
                    "url": url,
                })
                counter += 1
    return services

def parse_services(services):
    parsed_services = []
    for service in services:
        if "name" in service and "port" in service:
            name = service["name"]
            port = service["port"]
            type =service.get("type",infer_type(name, port))  
            url = generate_url(host_ip, port, type)
            parsed_services.append({
                "id": service.get("id", f"service-{len(parsed_services) + 1}"),
                "name": name,
                "ip": host_ip,
                "port": port,
                "type": type,
                "url": url,
            })
    return parsed_services



def check_service_status(service):
    url = service.get("url")
    host = service.get("ip")
    port = service.get("port")
    result = service.copy()

    try:
        response = requests.get(url, timeout=TIMEOUT_MS)
        status_code = response.status_code

        if status_code == 200:
            result["status"] = STATUS_RUNNING
        elif status_code in [401, 403] or not response.content:
            result["status"] = STATUS_WARNING
        elif status_code >= 500:
            result["status"] = STATUS_ERROR
        else:
            result["status"] = STATUS_WARNING
    except requests.Timeout: 
            result["status"] = STATUS_STOPPED
    except Exception as e:
        if(sendPing(host, port, TIMEOUT_MS / 1000)):
            result["status"] = STATUS_RUNNING
        else:
            result["status"] = STATUS_ERROR
    return result
