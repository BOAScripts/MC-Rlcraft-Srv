import os
import shutil
import datetime

# Backup the 'World' folder
timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup_dir = '/home/mcuser/world-backups'
world_dir = '/home/mcuser/mc-server/World'

# Create a compressed backup
backup_filename = f'World_{timestamp}'
backup_path = os.path.join(backup_dir, backup_filename)
shutil.make_archive(backup_path, 'gztar', world_dir)

# Retention: Maintain only 3 most recent backups
backup_list = sorted([f for f in os.listdir(backup_dir) if f.startswith('World_')], reverse=True)
keep_backups = 3

# Remove excess backups
if len(backup_list) > keep_backups:
    excess_backups = backup_list[keep_backups:]
    for backup in excess_backups:
        os.remove(os.path.join(backup_dir, backup))
