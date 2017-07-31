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
        #    MENUS DEFINITIONS
        # =======================

        # Menu definition
        self.menu_actions = {
            'main_menu': self.main_menu,
            # '1': menu1,
            # '2': menu2,
            # '3': menu3,
            '*': self.back,
            '0': self.exit,
        }

        self.options = []



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

        self.options = [(row[0],row[1],row[2]) for row in cur.fetchall()]
        cur.close()

        return

    # =======================
    #     MENUS FUNCTIONS
    # =======================

    # Crear Main Menu con información de BD
    def main_menu(self):
        self.DBGetNetworkElements()

        os.system('clear')
        print "Welcome,\n"
        print "Please choose the menu you want to start:"
        # print "1. Menu 1"
        # print "2. Menu 2"
        # print "3. Menu 3"

        for i in range(len(self.options)) :
            print ("%s. %s"%(i+1, self.options[i][0]))

        print "\n0. Quit"
        choice = raw_input(" >>  ")
        self.exec_menu(choice)

        return

    # Execute menu
    def exec_menu(self, choice):
        os.system('clear')
        ch = choice.lower()
        if ch == '':
            self.menu_actions['main_menu']()
        else:
            try:
                self.menu_actions[ch]()
            except KeyError:
                print "Invalid selection, please try again.\n"
                self.menu_actions['main_menu']()
        return

    # Menu 1
    def menu1(self):
        print "Hello Menu 1 !\n"
        print "*. Back"
        print "0. Quit"
        choice = raw_input(" >>  ")
        self.exec_menu(choice)
        return


    # Menu 2
    def menu2(self):
        print "Hello Menu 2 !\n"
        print "*. Back"
        print "0. Quit"
        choice = raw_input(" >>  ")
        self.exec_menu(choice)
        return

    def menu3():
        os.system("lssh 10.118.181.126")

        self.main_menu()
        return

    # Back to main menu
    def back(self):
        self.menu_actions['main_menu']()

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
