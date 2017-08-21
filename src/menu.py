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
        self.DBGetNetworkElements()

        os.system('clear')
        text =  ["Welcome %s,\n"%self.full_name]
        text.append("Please choose the menu you want to start:")
        text.append("1. Platforms filtered by Vendor")
        text.append("2. Platforms filtered by Location")
        text.append("3. All Platform")
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
                    self.menuPlatformVendors()
                elif ch == '2':
                    self.menuPlatformsLocations()
                elif ch == '3':
                    self.menuPlatformsAll()

            except KeyError:
                print "Invalid selection, please try again.\n"
                self.main_menu()
        return

    # Execute menu
    def exec_menu(self, choice):
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
                else:
                    try:
                        indice = int(choice)-1

                        self.executeNE(self.network_elements[indice][0],
                                        self.network_elements[indice][1],
                                        self.network_elements[indice][2],
                                        self.network_elements[indice][3]
                                        )
                    except ValueError:
                        raise KeyError
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
        self.exec_menu(choice)
        return


    # Menu 2
    def menuPlatformsLocations(self):
        print "All Platforms filtered by type of Location:\n"
        print "*. Back"
        print "0. Quit"
        choice = raw_input(" >>  ")
        self.exec_menu(choice)
        return

    # Menu 3
    def menuPlatformsAll(self):
        os.system('clear')
        text =  ["All Platforms:\n"]
        text.append("Please choose the menu you want to start:")
        for i in range(len(self.network_elements)) :
            text.append("%s. %s"%(i+1, self.network_elements[i][0]))
        text.append("\n*. Back\n0. Quit")

        print '\n'.join(text)
        choice = raw_input(">>  ")

        self.exec_menu(choice)
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
