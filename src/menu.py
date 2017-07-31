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

# Acceso de Base de Datos
dbname = 'sa_dev'
host = 'localhost'
user = 'sa'
password = 'password'

def DBGetNetworkElements(username):
    try:
        conn = psycopg2.connect('dbname=%s user=%s host=%s password=%s'%(dbname, user, host, password))
    except:
        sys.stderr.write("ERR: Unable to connect to the database\n")
        sys.exit(0)

    cur = conn.cursor()

    cur.execute("""SELECT name, ip, port FROM network_elements WHERE id IN (
                    SELECT network_element_id FROM area_network_elements WHERE area_id=(
                        SELECT area_id FROM employees WHERE username='%s'
                    )
                )
                """%(username))

    options = [(row[0],row[1],row[2]) for row in cur.fetchall()]
    cur.close()

    return options


# Main definition - constants
menu_actions  = {}

# =======================
#     MENUS FUNCTIONS
# =======================

# Main menu
def main_menu():
    os.system('clear')

    print "Welcome,\n"
    print "Please choose the menu you want to start:"
    print "1. Menu 1"
    print "2. Menu 2"
    print "3. Menu 3"
    print "\n0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)

    return

# Execute menu
def exec_menu(choice):
    os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    return

# Menu 1
def menu1():
    print "Hello Menu 1 !\n"
    print "9. Back"
    print "0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return


# Menu 2
def menu2():
    print "Hello Menu 2 !\n"
    print "9. Back"
    print "0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def menu3():
    os.system("lssh 10.118.181.126")

    main_menu()
    return

# Back to main menu
def back():
    menu_actions['main_menu']()

# Exit program
def exit():
    sys.exit()

# =======================
#    MENUS DEFINITIONS
# =======================

# Menu definition
menu_actions = {
    'main_menu': main_menu,
    '1': menu1,
    '2': menu2,
    '3': menu3,
    '9': back,
    '0': exit,
}

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
        main_menu()
        #print DBGetNetworkElements(username)
