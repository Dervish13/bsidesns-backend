.include <name.py>

SYSPKG = YES
USE_FREENIT = YES
SERVICE != echo ${app_name}
REGGAE_PATH := /usr/local/share/reggae

shell: up
	@sudo cbsd jexec user=devel jname=${SERVICE} /usr/src/bin/shell.sh

.include <${REGGAE_PATH}/mk/service.mk>
