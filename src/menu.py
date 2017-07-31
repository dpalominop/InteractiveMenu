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
import sys, os, getpass
import psycopg2

class Menu:
    """
        Creación dinámica de Menu basado en Base de Datos
    """

    def __init__(self, username):
        self.username = username

        # Acceso de Base de Datos
        self.dbCredential = {
            'dbname':'sa_dev',
            'host' :'localhost',
            'user' :'sa',
            'password':'password',
        }

    # =======================
    #     DATABASE FUNCTIONS
    # =======================

    def DBGetNetworkElements(self):
        try:
            conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(self.dbCredential['dbname'],
                                                                             self.dbCredential['user'],
                                                                             self.dbCredential['host'],
                                                                             self.dbCredential['password'])
                                    )
        except:
            sys.stderr.write("ERR: Unable to connect to the database\n")
            sys.exit(0)

        cur = conn.cursor()

        cur.execute("""SELECT name, ip, port FROM network_elements WHERE id IN (
                        SELECT network_element_id FROM area_network_elements WHERE area_id=(
                            SELECT area_id FROM employees WHERE username='%s'
                        )
                    )
                    """%(self.username))

        self.network_elements = [(row[0],row[1],row[2] or 22) for row in cur.fetchall()]
        cur.close()

        return

    # =======================
    #     MENUS FUNCTIONS
    # =======================

    # Crear Main Menu con información de BD
    def main_menu(self):
        self.DBGetNetworkElements()

        os.system('clear')
        text =  ["Welcome,\n"]
        text.append("Please choose the menu you want to start:")
        for i in range(len(self.network_elements)) :
            text.append("%s. %s"%(i+1, self.network_elements[i][0]))
        text.append("\n0. Quit")

        print '\n'.join(text)
        choice = raw_input(">>  ")

        self.exec_menu(choice)

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
                    self.menu_n(self.network_elements[int(choice)-1][1], self.network_elements[int(choice)-1][2])
            except KeyError:
                print "Invalid selection, please try again.\n"
                self.main_menu()
        return

    # # Menu 1
    # def menu1(self):
    #     print "Hello Menu 1 !\n"
    #     print "*. Back"
    #     print "0. Quit"
    #     choice = raw_input(" >>  ")
    #     self.exec_menu(choice)
    #     return
    #
    #
    # # Menu 2
    # def menu2(self):
    #     print "Hello Menu 2 !\n"
    #     print "*. Back"
    #     print "0. Quit"
    #     choice = raw_input(" >>  ")
    #     self.exec_menu(choice)
    #     return

    def menu_n(self, ip, port):
        os.system("lssh %s:%i"%(ip, port))

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
