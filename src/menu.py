#!/usr/bin/env python
# -*- coding: utf-8 -*-
#title           :menu.py
#description     :This program displays an interactive menu on CLI
#author          :Daniel Palomino
#email           :dapalominop@gmail.com
#date            :
#version         :0.1
#usage           :python menu.py
#notes           :
#python_version  :2.7.6
#=======================================================================

# Import the modules needed to run the script.
import sys, os, getpass, socket
import psycopg2
from datetime import datetime

class dotdict(dict):
    def __getattr__(self, name):
        return self[name]

class Menu:
    """
        Creación dinámica de Menu basado en Base de Datos
    """

    def __init__(self, username):
        self.username = username

        # Acceso de Base de Datos
        self.readConfigFile()

    def readConfigFile(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        try:
            config.read("/etc/lssh.conf")
            self.credential = {
                'db_dbname':'sa_dev',
                'db_hostname' :'localhost',
                'db_username' :'sa',
                'db_password':'password',

                'sf_hostname' :'localhost',
                'sf_username' :'sa',
                'sf_password':'password',
            }
            try:
                options = config.options('database')
                if 'database' in options:
                    self.credential['db_dbname'] = config.get('database', 'database')
                if 'hostname' in options:
                    self.credential['db_hostname'] = config.get('database', 'hostname')
                if 'username' in options:
                    self.credential['db_username'] = config.get('database', 'username')
                if 'password' in options:
                    self.credential['db_password'] = config.get('database', 'password')

            except:
                print "Not exists section: database."

            try:
                options = config.options('fileserver')
                if 'hostname' in options:
                    self.credential['sf_hostname'] = config.get('fileserver', 'hostname')
                if 'username' in options:
                    self.credential['sf_username'] = config.get('fileserver', 'username')
                if 'password' in options:
                    self.credential['sf_password'] = config.get('fileserver', 'password')

            except:
                print "Not exists section: serverfile."
        except:
            print "File /etc/lssh.conf not found."

    # =======================
    #     DATABASE FUNCTIONS
    # =======================
    def DBGetDirLog(self):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                             self.credential['db_username'],
                                                                             self.credential['db_hostname'],
                                                                             self.credential['db_password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()
        cur.execute("SELECT history_file FROM default_permissions")
        self.dir_log = ([row[0] for row in cur.fetchall() if row] or ["/var/log/sa"])[0]
        cur.close()

        return

    def DBGetUserFullName(self):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                             self.credential['db_username'],
                                                                             self.credential['db_hostname'],
                                                                             self.credential['db_password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()
        cur.execute("SELECT name FROM employees WHERE username='%s'"%(self.username))
        self.full_name = ([row[0] for row in cur.fetchall() if row] or ["Anónimo"])[0]
        cur.close()

        return

    def DBGetSurveillance(self):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                             self.credential['db_username'],
                                                                             self.credential['db_hostname'],
                                                                             self.credential['db_password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()
        cur.execute("""SELECT name FROM surveillances WHERE id=(
                        SELECT surveillance_id FROM employees WHERE username='%s'
                    )"""%(self.username))
        self.surveillance = ([row[0] for row in cur.fetchall() if row] or ["None"])[0]
        cur.close()

        return

    def DBGetIntro(self):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                             self.credential['db_username'],
                                                                             self.credential['db_hostname'],
                                                                             self.credential['db_password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()
        cur.execute("SELECT intro FROM default_permissions")
        self.intro = ([row[0] for row in cur.fetchall() if row] or [""])[0]
        cur.close()

    def DBGetRegisterNameById(self, ids, model=''):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                             self.credential['db_username'],
                                                                             self.credential['db_hostname'],
                                                                             self.credential['db_password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()
        query = "SELECT name FROM %s "%(model)

        cur.execute(query+"WHERE id IN %s", (tuple(ids),))
        name_regs = [row[0] for row in cur.fetchall() if row]
        cur.close()
        return name_regs

    def DBGetPlatforms(self, location=[], vendor=[], state=[]):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                             self.credential['db_username'],
                                                                             self.credential['db_hostname'],
                                                                             self.credential['db_password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()

        query1 = """SELECT ne.name, ne.ip, ne.port,
                            pr.name,
                            tp.name,
                            sy.name,
                            pl.name, pl.vendor_id, ne.location_id
                        FROM network_elements AS ne,
                            protocols AS pr,
                            types AS tp,
                            systems AS sy,
                            platforms AS pl
                        WHERE (ne.platform_id, ne.system_id, ne.type_id) IN (
                            SELECT platform_id, system_id, type_id FROM command_lists WHERE id IN (
                                SELECT command_list_id FROM command_list_employees WHERE employee_id=(
                                    SELECT id FROM employees WHERE username=%s
                                )
                            )
                        )
                    """
        query2 = """
                    AND pr.id = ne.protocol_id
                    AND tp.id = ne.type_id
                    AND sy.id = ne.system_id
                    AND pl.id = ne.platform_id
                    """
        args = (self.username,)

        if not location and not vendor and not state:
            query = query1 + query2
            args = (self.username,)
        elif not location and not vendor and state:
            query = query1 + "AND pl.state_id IN %s" + query2
            args = (self.username, tuple(state))
        elif not location and vendor and not state:
            query = query1 + "AND ne.vendor_id IN %s" + query2
            args = (self.username, tuple(vendor))
        elif not location and vendor and state:
            query = query1 + "AND ne.vendor_id IN %s AND pl.state_id IN %s" + query2
            args = (self.username, tuple(vendor), tuple(state))
        elif location and not vendor and not state:
            query = query1 + "AND ne.location_id IN %s" + query2
            args = (self.username, tuple(location))
        elif location and not vendor and state:
            query = query1 + "AND ne.location_id IN %s AND pl.state_id IN %s" + query2
            args = (self.username, tuple(location), tuple(state))
        elif location and vendor and not state:
            query = query1 + "AND ne.location_id IN %s AND ne.vendor_id IN %s" + query2
            args = (self.username, tuple(location), tuple(vendor))
        elif location and vendor and state:
            query = query1 + "AND ne.location_id IN %s AND ne.vendor_id IN %s AND pl.state_id IN %s" + query2
            args = (self.username, tuple(location), tuple(vendor), tuple(state))

        cur.execute(query, args)

        nes = cur.fetchall()
        self.platforms = {}
        for ne in nes:
            if ne[6] in self.platforms:
                if ne[5] in self.platforms[ne[6]]:
                    if ne[4] in self.platforms[ne[6]][ne[5]]:
                        self.platforms[ne[6]][ne[5]][ne[4]][ne[0]] = {'name':ne[0],
                                                                      'ip':ne[1],
                                                                      'port':ne[2],
                                                                      'protocol':ne[3]
                                                                      }
                    else:
                        self.platforms[ne[6]][ne[5]][ne[4]] = {ne[0]:{'name':ne[0],
                                                                      'ip':ne[1],
                                                                      'port':ne[2],
                                                                      'protocol':ne[3]
                                                                      }
                                                               }
                else:
                    self.platforms[ne[6]][ne[5]] = {ne[4]: {ne[0]:{'name':ne[0],
                                                                   'ip':ne[1],
                                                                   'port':ne[2],
                                                                   'protocol':ne[3]
                                                                   }
                                                            }
                                                    }
            else:
                self.platforms[ne[6]] = {ne[5]: {ne[4]: {ne[0]:{'name':ne[0],
                                                                'ip':ne[1],
                                                                'port':ne[2],
                                                                'protocol':ne[3]
                                                                }
                                                         }
                                                 }
                                         }
        cur.close()

        return self.platforms

    def DBSetLogRegister(self, employee, network_element, server, initiation, logfile, timestamp):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                             self.credential['db_username'],
                                                                             self.credential['db_hostname'],
                                                                             self.credential['db_password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()

        cur.execute("SELECT id FROM employees WHERE username = '%s'"%(employee))
        employee_id = cur.fetchall()[0][0]

        cur.execute("SELECT id FROM network_elements WHERE name = '%s'"%(network_element))
        network_element_id = cur.fetchall()[0][0]

        cur.execute("SELECT id FROM servers WHERE hostname = '%s'"%(server))
        server_id = cur.fetchall()[0][0]

        query = """INSERT INTO sessions (document_updated_at, created_at,
                                        updated_at,
                                        employee_id, network_element_id,
                                        server_id, initiation,
                                        document_file_name, document_content_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        data = (timestamp, timestamp, timestamp,
                employee_id, network_element_id,
                 server_id, initiation,
                 logfile, 'text/plain')

        cur.execute(query, data)

        try:
            conn.commit()
            conn.close()
        except:
            print "Unable to make commit"

        return


    # =======================
    #     MENUS FUNCTIONS
    # =======================

    # Crear Main Menu con información de BD
    def main_menu(self):
        self.DBGetDirLog()
        self.DBGetUserFullName()
        self.DBGetSurveillance()
        self.DBGetIntro()

        os.system('clear')
        text =  ["\033[93mBienvenido Sr(a). %s,\033[0m\n"%self.full_name]
        text.append('\033[94m'+self.intro+'\033[0m\n')
        # text.append("\033[91mAcepta? (s)í o (n)o\033[0m")
        print '\n'.join(text)
        ans = raw_input("\033[91mAcepta? (s)í o (n)o:  \033[0m")
        self.getAnswer(ans)
        return

    #Choice Menu
    def getAnswer(self, ans):
        os.system('clear')

        ch = ans.lower()
        if ch == '':
            self.main_menu()
        else:
            try:
                if ch == 'n':
                    self.exit()
                elif ch == 's':
                    self.printMenu()
                else:
                    self.main_menu()

            except KeyError:
                print "Invalid selection, please try again.\n"
                self.main_menu()
        return

    def getInteractiveOption(self, message='', model=''):
        # os.system('clear')
        uinput = raw_input('\033[93m'+message+'\033[0m')
        if uinput == '':
            return []
        else:
            try:
                conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.credential['db_dbname'],
                                                                                 self.credential['db_username'],
                                                                                 self.credential['db_hostname'],
                                                                                 self.credential['db_password'])
                                        )
            except:
                sys.stderr.write("ERR: Unable to connect to the database\n")
                sys.exit(0)

            cur = conn.cursor()
            cur.execute("SELECT id FROM %s WHERE name ~* '.*%s.*'"%(model, uinput))

            return [int(el[0]) for el in cur.fetchall() if el]

    def printMenu(self, ltype='', system='', platform='', location=[], vendor=[], state=[]):
        os.system('clear')
        self.DBGetPlatforms(location=location, vendor=vendor, state=state)

        text = []
        obj = None
        if ltype:
            text.append("""\033[94m
                        ####################################
                        Plataforma:\t%s
                        Sistema:\t%s
                        Tipo:\t\t%s
                        ####################################
                        \033[0m"""%(platform, system, ltype))
            text.append("""
                        \033[94mElementos de Red:\033[0m

                        """)
            try:
                obj = self.platforms[platform][system][ltype]
            except:
                obj = {}

        elif system:
            text.append("""\033[94m
                        ####################################
                        Plataforma:\t%s
                        Sistema:\t%s
                        ####################################
                        \033[0m"""%(platform, system))
            text.append("""
                        \033[94mTipos:\033[0m

                        """)
            try:
                obj = self.platforms[platform][system]
            except:
                obj = {}
        elif platform:
            text.append("""\033[94m
                        ####################################
                        Plataforma:\t%s
                        ####################################
                        \033[0m"""%(platform))
            text.append("""
                        \033[94mSistemas:\033[0m

                        """)
            try:
                obj = self.platforms[platform]
            except:
                obj = {}
        else:
            text.append("""\033[94m
                        ######################################
                        Plataformas de %s
                        ######################################
                        \033[0m"""%(self.surveillance))
            text.append("""
                        \033[94mPlataformas:\033[0m

                        """)
            obj = self.platforms

        if location:
            text.append("""\t\t\t\033[92mUbicación: %s\033[0m"""%self.DBGetRegisterNameById(location, model='locations'))
        if vendor:
            text.append("""\t\t\t\033[92mFabricante: %s\033[0m"""%self.DBGetRegisterNameById(vendor, model='vendors'))
        if state:
            text.append("""\t\t\t\033[92mEstado: %s\033[0m"""%self.DBGetRegisterNameById(state, model='states'))
        if location or vendor or state:
            text.append("\n")

        keys = obj.keys()
        for i in range(len(keys)):
            text.append("""\t\t\t\033[93m[%i] %s\033[0m"""%(i+1, keys[i]))
        text.append("""

                    \033[92m\tAgrupar por:\033[0m""")
        text.append("""\t\t\033[92m\t[u] Ubicación | [f] Fabricante | [e] Estado\033[0m
                    """)
        text.append("""
                    \033[91m\t[v] Volver
                    \t[s] Salir\033[0m
                    """)
        print '\n'.join(text)

        choice = raw_input("""\t\t\t\033[94mIngrese la opción deseada >>  \033[0m""")

        if choice not in ['v','u','f', 'e', 's', 'V', 'U','F', 'E','S']+[str(i+1) for i in range(len(keys))]:
            self.printMenu(ltype=ltype, system=system, platform=platform, location=location, vendor=vendor, state=state)
        elif choice in ('s', 'S'):
            self.exit()
        elif choice in ('u', 'U'):
            filter_option = self.getInteractiveOption(message='\n\t\t\tUbicación:\n\t\t\t>> ', model='locations')
            self.printMenu(ltype=ltype, system=system, platform=platform, location=filter_option, vendor=vendor, state=state)
        elif choice in ('f', 'F'):
            filter_option = self.getInteractiveOption(message='\n\t\t\tFabricante:\n\t\t\t>> ', model='vendors')
            self.printMenu(ltype=ltype, system=system, platform=platform, location=location, vendor=filter_option, state=state)
        elif choice in ('e','E'):
            filter_option = self.getInteractiveOption(message='\n\t\t\tEstado:\n\t\t\t>> ', model='states')
            self.printMenu(ltype=ltype, system=system, platform=platform, location=location, vendor=vendor, state=filter_option)
        elif choice in ('v','V'):
            if ltype:
                self.printMenu(ltype='', system=system, platform=platform, location=location, vendor=vendor, state=state)
            elif system:
                self.printMenu(ltype='', system='', platform=platform, location=location, vendor=vendor, state=state)
            elif platform:
                self.printMenu(ltype='', system='', platform='', location=location, vendor=vendor, state=state)
            else:
                self.main_menu()
        else:
            self.choiceOption(keys[int(choice)-1], ltype=ltype, system=system, platform=platform, location=location, vendor=vendor, state=state)
        return

    def choiceOption(self, option, ltype='', system='', platform='', location='', vendor='', state=''):
        try:
            obj = None
            if ltype:
                obj = dotdict(self.platforms[platform][system][ltype][option])
                self.executeNE(obj.name, obj.ip, obj.port, obj.protocol)
                self.printMenu(ltype=ltype, system=system, platform=platform, location=location, vendor=vendor, state=state)
            elif system:
                self.printMenu(ltype=option, system=system, platform=platform, location=location, vendor=vendor, state=state)
            elif platform:
                self.printMenu(ltype='', system=option, platform=platform, location=location, vendor=vendor, state=state)
            else:
                self.printMenu(ltype='', system='', platform=option, location=location, vendor=vendor, state=state)

        except Exception:
            print "Err: choiceOption"
            self.printMenu(ltype=ltype, system=system, platform=platform, location=location, vendor=vendor, state=state)
        return

    def executeNE(self, ne_name, ip, port, protocol):
        # os.system('clear')
        import unidecode

        timestamp = datetime.utcnow()
        zone_time = datetime.now()
        logfile = "%s-%s-%s-%s"%(zone_time.strftime("%Y-%m-%d-%H-%M-%S"),
                                self.username,
                                ip,
                                socket.gethostname()
                                )
        import unidecode
        logfile = unidecode.unidecode(unicode(logfile, 'utf-8'))

        ssh_log = "sshpass -p '%s' ssh %s@%s tee -a %s/%s"%(self.credential['sf_password'],
                                                              self.credential['sf_username'],
                                                              self.credential['sf_hostname'],
                                                              self.dir_log,
                                                              logfile
                                                            )

        self.DBSetLogRegister(self.username, ne_name,
                              socket.gethostname(), zone_time,
                              logfile, timestamp)

        if protocol == 'ssh':
            os.system("lssh %s:%i | %s"%(ip, port, ssh_log))
        elif protocol == 'telnet':
            os.system("telnet -e %s %i | %s"%(ip, port, ssh_log))
        else:
            os.system("%s %s:%i | %s"%(protocol, ip, port, ssh_log))

        return

    # Back to main menu
    def back(self):
        self.main_menu()

    # Exit program
    def exit(self):
        sys.exit()

# =======================
#      MAIN PROGRAM
# =======================

import signal

def exit_gracefully(signum, frame):
    print ''
    sys.exit(1)

# Main Program
if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)
    username = getpass.getuser()

    if username == 'root':
        os.system('/bin/bash')
    else:
        # Launch main menu
        menu = Menu(username)
        menu.main_menu()
