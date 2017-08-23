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
        self.dir_log = ([row[0] for row in cur.fetchall()] or ["/var/log/sa"])[0]
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
        self.full_name = ([row[0] for row in cur.fetchall()] or ["Anónimo"])[0]
        cur.close()

        return

    def DBGetNetworkElements(self):
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

        cur.execute("""SELECT ne.name, ne.ip, ne.port, pr.name AS protocol
                        FROM network_elements AS ne, protocols AS pr WHERE ne.id IN (
                            SELECT network_element_id FROM command_lists WHERE id IN (
                                SELECT command_list_id FROM command_list_employees WHERE employee_id=(
                                    SELECT id FROM employees WHERE username='%s'
                                )
                            )
                        ) AND pr.id = ne.protocol_id
                    """%(self.username)
                    )

        self.network_elements = [(row[0],row[1],row[2], row[3]) for row in cur.fetchall()]
        cur.close()

        return

    def DBGetMenu(self):
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

        cur.execute("""SELECT ne.name, ne.ip, ne.port,
                            pr.name,
                            tp.name,
                            sy.name,
                            pl.name, pl.vendor_id, pl.location_id
                        FROM network_elements AS ne,
                            protocols AS pr,
                            types AS tp,
                            systems AS sy,
                            platforms AS pl
                        WHERE ne.id IN (
                            SELECT network_element_id FROM command_lists WHERE id IN (
                                SELECT command_list_id FROM command_list_employees WHERE employee_id=(
                                    SELECT id FROM employees WHERE username='%s'
                                )
                            )
                        ) AND pr.id = ne.protocol_id
                        AND tp.id = ne.type_id
                        AND sy.id = tp.system_id
                        AND pl.id = sy.platform_id
                    """%(self.username)
                    )

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
        # self.DBGetNetworkElements()
        self.DBGetMenu()

        os.system('clear')
        text =  ["Welcome %s,\n"%self.full_name]
        text.append("Please choose the menu you want to start:")
        text.append("1. All Platform")
        text.append("2. Platforms filtered by Vendor")
        text.append("3. Platforms filtered by Location")
        text.append("\n0. Quit")
        print '\n'.join(text)

        choice = raw_input(">>  ")
        self.choiceMenu(choice)
        return

    #Choice Menu
    def choiceMenu(self, choice):
        os.system('clear')
        ch = choice.lower()
        if ch == '':
            self.main_menu()
        else:
            try:
                if ch == '0':
                    self.exit()
                elif ch == '*':
                    self.back()
                elif ch == '1':
                    # self.menuPlatformsAll()
                    self.printMenu()
                elif ch == '2':
                    self.menuPlatformVendors()
                elif ch == '3':
                    self.menuPlatformLocations()

            except KeyError:
                print "Invalid selection, please try again.\n"
                self.main_menu()
        return

    # Menu 1
    def menuPlatformVendors(self):
        print "All Platforms filtered by type of Vendor:\n"
        print "*. Back"
        print "0. Quit"
        choice = raw_input(" >>  ")
        self.printMenu(choice)
        return

    # Menu 2
    def menuPlatformLocations(self):
        print "All Platforms filtered by type of Location:\n"
        print "*. Back"
        print "0. Quit"
        choice = raw_input(" >>  ")
        self.printMenu(choice)
        return

    def printMenu(self, ltype='', system='', platform=''):
        os.system('clear')
        text = []
        obj = None
        if ltype:
            text.append("Please choose the NE:\n")
            obj = self.platforms[platform][system][ltype]
        elif system:
            text.append("Please choose the Type:\n")
            obj = self.platforms[platform][system]
        elif platform:
            text.append("Please choose the System:\n")
            obj = self.platforms[platform]
        else:
            text.append("All Platforms:\nPlease choose the platform:\n")
            obj = self.platforms

        keys = obj.keys()
        for i in range(len(keys)):
            text.append("%i. %s"%(i+1, keys[i]))
        text.append("\n*. Back\n0. Quit")

        print '\n'.join(text)
        choice = raw_input(">>  ")

        if choice not in ['*','0']+[str(i+1) for i in range(len(keys))]:
            self.printMenu(ltype=ltype, system=system, platform=platform)
        elif choice == '0':
            self.exit()
        elif choice == '*':
            if ltype:
                self.printMenu(ltype='', system=system, platform=platform)
            elif system:
                self.printMenu(ltype='', system='', platform=platform)
            elif platform:
                self.printMenu(ltype='', system='', platform='')
            else:
                self.main_menu()
        else:
            self.choiceOption(keys[int(choice)-1], ltype=ltype, system=system, platform=platform)
        return

    def choiceOption(self, option, ltype='', system='', platform=''):
        os.system('clear')
        try:
            obj = None
            if ltype:
                obj = dotdict(self.platforms[platform][system][ltype][option])
                self.executeNE(obj.name, obj.ip, obj.port, obj.protocol)
            elif system:
                self.printMenu(ltype=option, system=system, platform=platform)
            elif platform:
                self.printMenu(ltype='', system=option, platform=platform)
            else:
                self.printMenu(ltype='', system='', platform=option)

        except Exception:
            self.printMenu(ltype=ltype, system=system, platform=platform)
        return

    def executeNE(self, ne_name, ip, port, protocol):
        timestamp = datetime.utcnow()
        zone_time = datetime.now()
        logfile = "%s-%s-%s-%s"%(zone_time.strftime("%Y-%m-%d-%H-%M-%S"),
                                self.username,
                                ne_name,
                                socket.gethostname()
                                )

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

        self.main_menu()
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

# Main Program
if __name__ == "__main__":

    username = getpass.getuser()

    if username == 'root':
        os.system('/bin/bash')
    else:
        # Launch main menu
        menu = Menu(username)
        menu.main_menu()
