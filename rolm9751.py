#!/usr/bin/env python

import socket, threading, sys, signal, ssl, time
import sqlite3

HOST = ''
PORT = 2323
VERSION = '0.2'
ROLMDB = 'rolm9751.db'

CBXPASS = 'PASSWORD'
CBXMOD = '40'
CBXID = 'EDISO34872'
CBXNODE = '01'
CBXRAM = '16'
CBXROM = '4.2'
CBXREL = '9005.6.84'
CBXTEMP = '29'

print '\033[92mRolm 9751 simulator version ' + VERSION + ' starting up.\n'

try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
        print '\033[91mError creating socket: ' + str(msg[0]) + ': ' + msg[1]
        sys.exit()

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(4)

lock = threading.Lock()

print 'Waiting for connections on port ' + str(PORT) + '...\n\033[0m'
def CBXTIME():
	return time.strftime("%H:%M:%S")

def CBXDATE():
	return time.strftime("%A %x")

def CBXDATE2():
	return time.strftime("%x")

def CLI_LI(sck,cmd):
	if cmd == 'LI ?':
		sck.socket.send('\n  ENTER: \n')
		sck.socket.send('    ACD                ACDDB              AFACTS\n')
		sck.socket.send('    ALARMS             ALPEXC             ALPSTATE\n')
		sck.socket.send('    AP                 BADTS              BUS_STAT\n')
		sck.socket.send('    CACHE              CARDTRACE          CARD_RESET\n')
		sck.socket.send('    CAS                CDR                CDRTRAF\n')
		sck.socket.send('    CLKERRS            CLKNODES           CLKSOURCE\n')
		sck.socket.send('    CLKSTATUS          CMSTS              COMPATIBILITY\n')
		sck.socket.send('    CPN                CTH                CTS\n')
		sck.socket.send('    CYPET              DCMET              DIR\n')
		sck.socket.send('    DISABLE            DOWN               ERRH\n')
		sck.socket.send('    ERRORS             EXCEPTIONS         FILE\n')
		sck.socket.send('    FIRMWARE_LEVEL     FL                 HD\n')
		sck.socket.send('    INL_STATUS         LOC                MODL\n')
		sck.socket.send('    MW                 NIEP               NOCALL_STATUS\n')
		sck.socket.send('    NONRED_IPL         OPTIONS            PADTRACE\n')
		sck.socket.send('    PATCH              PERM_DATA_CONNECT  PMS_PEGS\n')
		sck.socket.send('    PORT               RCT                REPDL\n')
		sck.socket.send('    ROLL               RP                 RPDN\n')
		sck.socket.send('    RPET               RTRAF              SAVE\n')
		sck.socket.send('    SIO_PORT           STASP              STATISTICS\n')
		sck.socket.send('    STATUS             TEMPERATURE        TEST\n')
		sck.socket.send('    TIME               TRAF               TRAIL\n')
		sck.socket.send('    TRAPPED            TRUNK_NUM          TRUNK_STATUS\n')
		sck.socket.send('    TTI_STATUS         TX                 VOL\n')
		sck.socket.send('    XDI                XDIACTIVE\n\n')
		sck.socket.send('NOUN: ')

		cmd2 = sck.socket.recv(128).strip()
	elif cmd.startswith('LI ERRH'):
		sck.socket.send('PAD: ')
		cmd2 = sck.socket.recv(128).strip()
		sck.socket.send('LIST OPTION: ')
		cmd2 = sck.socket.recv(128).strip()
		sck.socket.send('ALL\n')             
		sck.socket.send('SHORT OR LONG: ')
		cmd2 = sck.socket.recv(128).strip()
		sck.socket.send('SHORT\n')
		sck.socket.send('\n TARGET  SOURCE  SYSTEM  ID   RELEASE   BIND DATE   CURRENT  DATE/TIME\n')
		sck.socket.send('    1       1    ' + CBXID + '  ' + CBXREL + '  27/JAN/98  ' + CBXDATE2() + '  ' + CBXTIME() + '\n')
		sck.socket.send(' ----------------------------------------------------------------------\n\n\n')
		sck.socket.send('                     TELEPHONY PROBLEM OVERVIEW\n')
		sck.socket.send('                     --------------------------\n')
		sck.socket.send('              LAST COMPLETELY CLEARED  17:47:44  APR-28-2015\n\n')
		sck.socket.send('   SMIOC         01/022202  FAILED   PRI = 030 (MAJOR) 1ST = 17:47 04/28\n\n')

	else:
		sck.socket.send('NOUN: ')
		cmd2 = sck.socket.recv(128).strip()

def CNFG(sck):
	sck.socket.send('                      CBX/9000\n')
        sck.socket.send('      INTERACTIVE   CONFIGURATION   INTERFACE\n\n')
	sck.socket.send(CBXTIME() + ' ON ' + CBXDATE() + '\n')

	CNFG_LOOP = True
	while CNFG_LOOP:
		sck.socket.send('COMMAND: ')
		CNFG_cmd = sck.socket.recv(128).strip().split(" ")
		if CNFG_cmd[0] == '':
			True
		elif CNFG_cmd[0] == '?':
			sck.socket.send('\n  ENTER: \n')
			sck.socket.send('    BYE      CHECK    COUNT    CREATE   DELETE   DONE\n')
			sck.socket.send('    EXIT     LIST     MODIFY   QUIT     REBUILD  RESET\n\n')
		elif CNFG_cmd[0].startswith('LI'):
			if len(CNFG_cmd) == 1:
				sck.socket.send('NOUN: ')
				CNFG_cmd2 = sck.socket.recv(128).strip().split(" ")
				if len(CNFG_cmd2) == 1:
					while CNFG_cmd2[0] == '?':
						CNFG_LI_Q(sck)
						CNFG_cmd2 = sck.socket.recv(128).strip().split(" ")
					if CNFG_cmd2[0] == 'EXTEN':
						sck.socket.send('EXTEN #: ')
						CNFG_cmd3 = sck.socket.recv(128).strip()
						CNFG_LI_EXTEN(sck,CNFG_cmd3)
					elif CNFG_cmd2[0] == 'LEX':
						True
					elif CNFG_cmd2 == 'RP':
						sck.socket.send('PAD:  ')
						CNFG_cmd3 = sck.socket.recv(128).strip()
						CNFG_LI_RP(sck,CNFG_cmd3)
					else:
						sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')
				if len(CNFG_cmd2) > 1:
					True
			elif len(CNFG_cmd) == 2:
                                if CNFG_cmd[1] == '?':
					CNFG_LI_Q(sck)
					CNFG_cmd2 = sck.socket.recv(128).strip().split(" ")
					if len(CNFG_cmd2) == 1:
						if CNFG_cmd2[0] == '?':
							CNFG_LI_Q(sck)
						elif CNFG_cmd2[0] == 'EXTEN':
							sck.socket.send('EXTEN #: ')
							CNFG_cmd3 = sck.socket.recv(128).strip()
							CNFG_LI_EXTEN(sck,CNFG_cmd3)
						elif CNFG_cmd2[0] == 'LEX':
							True
						elif CNFG_cmd2[0] == 'RP':
							sck.socket.send('PAD:  ')
							CNFG_cmd3 = sck.socket.recv(128).strip()
							CNFG_LI_RP(sck,CNFG_cmd3)
						else:
							sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')
					elif len(CNFG_cmd2) == 2:
						if CNFG_cmd2[0] == '?':
							CNFG_LI_Q(sck)
						elif CNFG_cmd2[0] == 'EXTEN':
							CNFG_LI_EXTEN(sck,CNFG_cmd2[1])
						elif CNFG_cmd2[0] == 'LEX':
							True
						elif CNFG_cmd2[0] == 'RP':
                                                        CNFG_LI_RP(sck,CNFG_cmd2[1])
						else:
							sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')
					else:
						sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')
				elif CNFG_cmd[1] == 'EXTEN':
	                                sck.socket.send('EXTEN #: ')
        	                        CNFG_cmd2 = sck.socket.recv(128).strip()
					CNFG_LI_EXTEN(sck,CNFG_cmd2)
				elif CNFG_cmd[1] == 'LEX':
					True
				elif CNFG_cmd[1] == 'RP':
					sck.socket.send('PAD:  ')
					CNFG_cmd2 = sck.socket.recv(128).strip()
					CNFG_LI_RP(sck,CNFG_cmd2)
				else:
					sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')
			elif len(CNFG_cmd) == 3:
				if CNFG_cmd[1] == 'EXTEN':
					CNFG_LI_EXTEN(sck,CNFG_cmd[2])
				elif CNFG_cmd[1] == 'LEX':
					True
				elif CNFG_cmd[1] == 'RP':
					CNFG_LI_RP(sck,CNFG_cmd[2])
				else:
					sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')	
			else:
				sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')
		
		elif (CNFG_cmd[0].startswith('BY') or CNFG_cmd[0].startswith('EX')):
			CNFG_LOOP = False
		else:
			sck.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')

def CNFG_LI_Q(sck):
	sck.socket.send('\n  ENTER: \n')
	sck.socket.send('    ACD_GROUP            ACD_ID               ACD_KTA\n')
	sck.socket.send('    ACD_MEMBER           ACD_ROUTE            ACD_SILENT\n')
	sck.socket.send('    AC_EXCEPTION         AFACTS_LIMITS        AFACTS_TRUNK_GROUP\n')
	sck.socket.send('    ATC                  ATC_GROUP            AUTO_CNFG_BACKUP\n')
	sck.socket.send('    AVAIL                BUTTON               CARD_PARAM\n')
	sck.socket.send('    CDR                  CDR_EXCLUDE          CLOCK_INPUTS\n')
	sck.socket.send('    CNFG_ERRORS          CNFG_NETWORK         CNFG_QUEUE\n')
	sck.socket.send('    CNFG_STATUS          CNFG_USERS           CNI_COS\n')
	sck.socket.send('    COM_GROUP            CONTROL_GROUPS       COS_FEAT\n')
	sck.socket.send('    COS_NUMBER           COUNTRY_CODE         CPN_HOST_TOPOLOGY\n')
	sck.socket.send('    CPN_PATHS            CPN_RING_TOPOLOGY    DATA_ACCESS\n')
	sck.socket.send('    DATA_DEVICE          DATA_GROUP           DATA_LINE\n')
	sck.socket.send('    DATA_NETWORK_ACCESS  DIGIT_TRAN           DNIS\n')
	sck.socket.send('    ETN_COS              EXPECTED_DIGITS      EXTEN\n')
	sck.socket.send('    EXTERNAL_ALARMS      FAC                  FACEPLATE\n')
	sck.socket.send('    FAC_TYPE             FAMILY               FEAT_CODE\n')
	sck.socket.send('    FIRST_DIGIT          HD_GROUP             INTL_BLOCKING\n')
	sck.socket.send('    INTL_SEARCH_SEQ      INTL_SERVICE_LIST    LEX\n')
	sck.socket.send('    LOGON_PROFILE        MAP                  MODEM_POOL\n')
	sck.socket.send('    NET_PLAN             NET_SERVICE          NORTH_PLAN\n')
	sck.socket.send('    OSP_BLOCKING         PARAM                PICK\n')
	sck.socket.send('    PMI                  PORT_COUNT           POWER\n')
	sck.socket.send('    POWER_SUPPLY         Q_TYPE               RB5250\n')
	sck.socket.send('    RD100                REXTEN               ROUTE_LIST\n')
	sck.socket.send('    RP                   RPDN                 RPS_ON\n')
	sck.socket.send('    SATOP_COS            SAT_NAME             SEARCH_SEQ\n')
	sck.socket.send('    SECTION              SECURITY_GROUP       SERVICE_LIST\n')
	sck.socket.send('    SIO_PORTS            SLI                  SPECIAL_DIGITS\n')
	sck.socket.send('    SPEED                TEN_DIGIT            TIMER_GROUP\n')
	sck.socket.send('    TIME_CHANGE          TOLL_EXCEPTION       TRAFFIC_LIMITS\n')
	sck.socket.send('    TRAF_INTERVAL        TRUNK                TRUNK_ACCESS\n')
	sck.socket.send('    TRUNK_GROUP          XDI_LINKS            XREF_D_CHAN\n')
	sck.socket.send('    XREF_TIMER_GROUP     XREF_TRUNK_GROUP\n\n')
	sck.socket.send('NOUN: ')

def CNFG_LI_EXTEN(sck,num):
	sql = sqlite3.connect(ROLMDB)
	cursor = sql.execute("SELECT * FROM ext WHERE extn = \'" + num + "\'")
	row = cursor.fetchone()
	if row == None:
		sck.socket.send('NO MATCH\n\n')
		return

	sck.socket.send('\n\n                                                        FORWARD  ON\n')
	sck.socket.send('                           SYSTEM        FORWARDING     BSY RNA DND\n')
	sck.socket.send('   EXTN    TYPE COS TARGET 1 TARGET 2 TARGET 3 TARGET 4 I E I E I E RINGDOWN\n')
	sck.socket.send('   ------- ---- --- -------- -------- -------- -------- - - - - - - --------\n')
	# EXTN
	sck.socket.send('DS '+ row[0])
	if len(row[0]) < 7:
		rowlen = 8 - len(row[0])
		for x in xrange(rowlen):
			sck.socket.send(' ')
	# TYPE
	sck.socket.send(row[1])
	if len(row[1]) < 4:
		rowlen = 5 - len(row[1])
		for x in xrange(rowlen):
			sck.socket.send(' ')
	# COS
	sck.socket.send(row[2])
        if len(row[2]) < 3:
                rowlen = 4 - len(row[2])
                for x in xrange(rowlen):
                        sck.socket.send(' ')
	# TARGET 1
	if row[3] is None:
		sck.socket.send('         ')
	else:
	       	sck.socket.send(row[3])
	        if len(row[3]) < 8:
	                rowlen = 9 - len(row[3])
	                for x in xrange(rowlen):
	                        sck.socket.send(' ')
	# TARGET 
	if row[4] is None:
		sck.socket.send('         ')
	else:
	        sck.socket.send(row[4])
	        if len(row[4]) < 8:
	                rowlen = 9 - len(row[4])
	                for x in xrange(rowlen):
	                        sck.socket.send(' ')
	# TARGET 3
	if row[5] is None:
		sck.socket.send('         ')
	else:
	        sck.socket.send(row[5])
	        if len(row[5]) < 8:
	                rowlen = 9 - len(row[5])
	                for x in xrange(rowlen):
	                        sck.socket.send(' ')
	# TARGET 4
        if row[6] is None:
                sck.socket.send('         ')
        else:
                sck.socket.send(row[6])
                if len(row[6]) < 8:
                        rowlen = 9 - len(row[6])
                        for x in xrange(rowlen):
                                sck.socket.send(' ')
	# FWD Busy Internal
	if row[7] is None:
		sck.socket.send('- ')
	else:
		sck.socket.send(row[7] + ' ')
	# FWD Busy External
        if row[8] is None:
                sck.socket.send('- ')
        else:
                sck.socket.send(row[8] + ' ')
	# FWD Ring No Answer Internal
        if row[9] is None:
                sck.socket.send('- ')
        else:
                sck.socket.send(row[9] + ' ')
	# FWD Ring No Answer External
        if row[10] is None:
                sck.socket.send('- ')
        else:
                sck.socket.send(row[10] + ' ')
	# FWD Do Not Disturb Internal
        if row[11] is None:
                sck.socket.send('- ')
        else:
                sck.socket.send(row[11] + ' ')
	# FWD Do Not Disturb External
        if row[12] is None:
                sck.socket.send('- ')
        else:
                sck.socket.send(row[12] + ' ')
	# Ringdown
	if row[13] is None:
		sck.socket.send('\n')
	else:
		sck.socket.send(row[13])

	sck.socket.send('\n\n   ACD NAME \n')
	sck.socket.send('    -  ----------------\n')

	sck.socket.send('DS  ')
	# ACD Y/N
	sck.socket.send(row[14] + '  ')
	# Display Name
	sck.socket.send(row[15] + '\n\n')

	sql.close()	

def CNFG_LI_LEX(sck,num):
	True
def CNFG_LI_RP(sck,num):
        sql = sqlite3.connect(ROLMDB)
        cursor = sql.execute("SELECT * FROM rp WHERE pad = \'" + num + "\'")
        row = cursor.fetchone()
        if row == None:
                sck.socket.send('NO MATCH\n\n')
                return

	sck.socket.send('\n\n                       D V                           S\n')
	sck.socket.send('                       A M                           P                   ACD\n')
	sck.socket.send('             RLID      T O  REF  TBL BUZZ            K D                 BSY HR\n')
	sck.socket.send('   PAD       TYPE      A D  NO.  NO. INTERCM VOICE C R T EXTN 1  R MW BI USAGE%\n')
	sck.socket.send('   --------- --------- - -- ---- --  ------- ------- - - ------- - -  -  ---\n')
	sck.socket.send('DS ' + CBXNODE + '/')
	# PAD address
	sck.socket.send(row[0] + ' ')
	# RLID type
	sck.socket.send(row[1])
	if len(row[1]) < 9:
		rowlen = 10 - len(row[1])
		for x in xrange(rowlen):
			sck.socket.send(' ')
	# DATA
	sck.socket.send(row[2] + ' ')
	# VMOD
	sck.socket.send(row[3] + ' ')
	# REF No.
	sck.socket.send(row[4])
        if len(row[4]) < 4:
                rowlen = 5 - len(row[4])
                for x in xrange(rowlen):
                        sck.socket.send(' ')
	# TBL No.
	sck.socket.send(row[5])
	if len(row[5]) < 2:
		rowlen = 4 - len(row[5])
		for x in xrange(rowlen):
			sck.socket.send(' ')
	# Buzz Intercom
        if row[6] is None:
                sck.socket.send('        ')
        else:
                sck.socket.send(row[6])
                if len(row[6]) < 7:
                        rowlen = 8 - len(row[6])
                        for x in xrange(rowlen):
                                sck.socket.send(' ')
	# Voice C
        if row[7] is None:
                sck.socket.send('        ')
        else:
                sck.socket.send(row[7])
                if len(row[7]) < 7:
                        rowlen = 8 - len(row[7])
                        for x in xrange(rowlen):
                                sck.socket.send(' ')
	# Speaker
	sck.socket.send(row[8] + ' ')
	# DT
	sck.socket.send(row[9] + ' ')
	# Extension 1
        if row[10] is None:
                sck.socket.send('       ')
        else:
                sck.socket.send(row[10])
                if len(row[10]) < 7:
                        rowlen = 8 - len(row[10])
                        for x in xrange(rowlen):
                                sck.socket.send(' ')
	# Ring
	sck.socket.send(row[11] + ' ')
	# Message Waiting Indicator
	sck.socket.send(row[12] + '  ')
	# Busy Indicator
	sck.socket.send(row[13] + '  ')
	# ACD Busy Usage
	sck.socket.send(row[14])
	if len(row[14]) < 3:
		rowlen = 3 - len(row[14])
		for x in xrange(rowlen):
			sck.socket.send(' ')
	sck.socket.send('\n\n')

	sck.socket.send('   CLLD \n')
	sck.socket.send('   NAME\n')
	sck.socket.send('   -\n')
	sck.socket.send('DS ')
	sck.socket.send(row[15] + '\n\n')
	sql.close()
class RolmServer(threading.Thread):
    def __init__(self, (socket,address)):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address= address

    def run(self):
        print '\033[92m-- \033[0mConnection detected from: \033[96m%s\033[0m:\033[96m%s\033[0m.' % self.address
	LOOP1 = True
	while LOOP1:
		self.socket.send('\n')
		self.socket.send('ROLM CBX  MODEL ' + CBXMOD + ', 9030B CPU (' + CBXRAM + 'M) (Prom Rev ' + CBXROM + ')  SITE ID: ' + CBXID +'\n')
		self.socket.send('RELEASE: ' + CBXREL + '  BIND DATE: 27/January/98     ' + CBXRAM + ' Megabytes\n')
		self.socket.send('(C) Copyright 1980-1998 Siemens Rolm Communications Inc. All rights reserved.\n')
		self.socket.send('ROLM is a registered trademark of Siemens Rolm Communications Inc.\n')
		self.socket.send(CBXTIME() + ' ON ' + CBXDATE() + '   ' + CBXTEMP + ' DEGREES C\n\n\n')
	
		LP_LOOP = True
		while LP_LOOP:
			self.socket.send('USERNAME: ')
			RUSER = self.socket.recv(128).strip()
			self.socket.send('PASSWORD: ')
			RPASS = self.socket.recv(128).strip()
			if (RUSER == 'SU' and RPASS == CBXPASS):
				LP_LOOP = False
			else:
				 self.socket.send('\nINVALID USERNAME-PASSWORD PAIR.\n\n')

		CLI_LOOP = True
		while CLI_LOOP:
			self.socket.send('% ')
			CLI_CMD = self.socket.recv(128).strip()
			if CLI_CMD == '':
				True
			elif CLI_CMD == '?':
				 self.socket.send('\n ENTER: \n')
				 self.socket.send('   ABORT       ACTIVATE    APPLY       BUILD       BYE         CANCEL\n')
				 self.socket.send('   CDT         CDT_INL     CHANGE      CLEAR       CNFG        COMPRESS\n')
				 self.socket.send('   COPY        CPEG        CXCON       CXNET       DCF         DDT\n')
				 self.socket.send('   DDT_INL     DEACTIVATE  DEFINE      DELETE      DEMOUNT     DIAG\n')
				 self.socket.send('   DISABLE     DMTST       DOWN        DX_TR       ENABLE      EXPAND\n')
				 self.socket.send('   FAULT_ISO   FINIT       FORMAT      FSD         HDBST       INSTALL\n')
				 self.socket.send('   IPLOAD      KILL        LIST        LOAD        LOGOFF      LOGON\n')
				 self.socket.send('   LPEG        MONITOR     MOUNT       NEXT        PAGE        PDIO\n')
				 self.socket.send('   QAT         QITM        QSTATUS     RECEIVE     REFERENCE   RENAME\n')
				 self.socket.send('   RESET       RESTART     RESTORE     REVERSE     RM          RMOFF\n')
				 self.socket.send('   ROLL        SEND        SET         SHOW        SITM        SSAT\n')
				 self.socket.send('   START       STATUS      STOP        SWITCHOVER  TEST        TKSTS\n')
				 self.socket.send('   TRANSLATE   UNCOMPRESS  UNLOCK      UNROLL      UP          VERIFY\n\n\n')

			elif CLI_CMD.startswith('BY'):
				CLI_LOOP = False
			elif CLI_CMD.startswith('LI'):
				CLI_LI(self,CLI_CMD)
			elif CLI_CMD.startswith('CN'):
				CNFG(self)
			elif CLI_CMD == 'X':
				self.socket.send('Exiting Rolm 9751 Emulator...\n')
				CLI_LOOP = False
				LOOP1 = False
			else:
				self.socket.send('ERROR: MNEMONIC IS NOT KNOWN - PLEASE RE-ENTER\n\n')


while True: # wait for socket to connect
        # send socket to chatserver and start monitoring
        RolmServer(s.accept()).start()
