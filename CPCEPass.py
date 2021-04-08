#!/usr/bin/python3
import os, crypt, subprocess, random, string, argparser

# Get arguments
def get_args():
    parser = argparse.ArgumentParser("Changing password of email user in cPanel.")
    parser.add_argument("-d", "--domain", dest="domain", help="Domain to change all email user password.")
    parser.add_argument("-p", "--passwd", dest="password", help="New password for all user in domain.")
    args = parser.parse_args()

    # Check argument value
    if not args.domain:
        exit("[-] No specified domain name. Using --help for more informaiton")
    elif not args.password:
        exit("[-] No specified password to change. Using --help for more information")
    else:
        return args.domain, args.password

# Check root privileges
def check_root():
    if os.geteuid() != 0:
        exit("[-] You need to have root privileges to run this script.")
    else:
        print("[+] Root check success.")

# Check server run cPanel
def check_cPanel():
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(["/usr/local/cpanel/cpanel", "-V"], stdout=FNULL, stderr=subprocess.STDOUT)
        print("[+] cPanel check success.")
    except subprocess.CalledProcessError:
        exit("[-] Server is not running cPanel.")

# Get owner of a domain
def get_owner(domain):
    user = None 
    with open("/etc/userdomains", "r") as f:
        for line in f:
            if line.startswith(domain):
                user = line.split(":")[-1].strip()
                print(f"[+] User of domain {domain} is {user}")
                return user
    if not user:
        exit(f"[-] Domain {domain} not found!") 

# Get home directory
def get_home_dir(user):
    home_dir = None
    with open("/etc/passwd", "r") as f:
        for line in f:
	if line.startswith(user):
                home_dir = line.split(":")[5]
                print(f"[+] Home directory of user {user} is {home_dir}")
                return home_dir
    if not home_dir:
        exit(f"[-] User {user} not found!")

# Generate password hash
def password_hash_gen(password):
    hasing_scheme_with_salt = "$6$" + "".join([random.choice(string.ascii_letters + string.digits) for _ in range(16)])
    new_hash = crypt.crypt(password, hasing_scheme_with_salt)
    return new_hash

def main():
    check_root()
    check_cPanel()

    domain, password = get_args()

    user = get_owner(domain)
    home_dir = get_home_dir(user)
    
    shadow_path = os.path.join(os.sep, homedir, "etc", domain, "shadow")
    print(f"[+] Set shadow path to {shadow_path}")
    new_shadow_content = []

    # Read and edit shadow file
    with open(shadow_path, "r") as s:
        shadow_content = s.readlines()
        for line in shadow_content:
            user_mail, old_hash = line.split(":")[0:2]
            new_hash = password_hash_gen(password)

            print(f"[+] Changing password email accout {user_mail}@{domain} to {new_hash}")
            input()
            line = line.replace(old_hash, new_hash)
            new_shadow_content.append(line)

    # Write and save shadow file
    new_shadow_content = ''.join(new_shadow_content)
    print(f"*** New shadow file ***\n{new_shadow_content}")
    input("Continue to proccess?")
    with open(shadow_path, "w") as s:
        s.write(new_shadow_content) 
    print("[+] Password has changed successfully.")

if __name__ == "__main__":
    main()
