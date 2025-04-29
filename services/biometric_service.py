from zk import ZK
from django.conf import settings

# Update with your actual device IP
DEVICE_IP = '192.168.1.201'  # example
DEVICE_PORT = 4370           # default port for ESSL

def register_member_on_biometric(member):
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=5)
    conn = None

    try:
        conn = zk.connect()
        conn.disable_device()

        existing_users = conn.get_users()
        if existing_users:
            new_user_id = max([user.user_id for user in existing_users]) + 1
        else:
            new_user_id = 1

        # Register the user on the biometric device
        conn.set_user(uid=new_user_id, name=f"{member.first_name} {member.last_name}")

        print(f"Successfully created user {new_user_id} on biometric device.")

        conn.enable_device()
        conn.disconnect()

        return new_user_id

    except Exception as e:
        print(f"Error during biometric registration: {e}")
        if conn:
            conn.disconnect()
        return None
