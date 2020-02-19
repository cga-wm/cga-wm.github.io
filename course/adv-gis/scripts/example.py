#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# example.py
#
# Tyler W. Davis, CGA, William & Mary, Williamsburg, VA
#
# LAST EDIT: 2020-02-17
#
# This is an example script for ADV GIS.
#
##############################################################################
# REQUIRED MODULES
##############################################################################
import datetime

###############################################################################
# FUNCTIONS
###############################################################################
def string_to_date(x):
    """
    Name:     string_to_date
    Input:    string (x)
    Output:   datetime.datetime (d)
    Features: Returns date object for a timestamp string
    """
    try:
        d = datetime.datetime.strptime(x, '%Y-%m-%d')
    except ValueError:
        # Take another crack at it:
        try:
            d = datetime.datetime.strptime(x, '%m/%d/%Y')
        except:
            raise ValueError("Error! Could not process date!")
    except:
        raise ValueError("Error! Could not process date!")
    else:
        return d.date()


##############################################################################
# CLASSES
##############################################################################
class Human(object):
    """
    Name:     Human
    Features: A demo class
    History:  Version 0.0
    """
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Parameters
    # ////////////////////////////////////////////////////////////////////////
    MAX_HEIGHT_FT = 9.0


    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Initialization
    # ////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
        Name:     Human.__init__
        Inputs:   None.
        Outputs:  None.
        Features: Initializes the Human class
        """
        self.name = None
        self.age = None
        self.dob = None

    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Function Definitions
    # ////////////////////////////////////////////////////////////////////////
    def hasName(self, human_name):
        """
        Name:     Human.hasName
        Inputs:   str, a name for your human (human_name)
        Outputs:  None.
        Features: Give your human a name
        """
        if self.name is not None:
            print("%s already has a name!" % self.name)
        else:
            self.name = human_name

    def hasAge(self, human_age):
        """
        Name:     Human.hasAge
        Inputs:   int/float, an age for your human (human_age)
        Outputs:  None.
        Features: Give your human an age
        """
        if self.age is not None and self.name is not None:
            print("%s already has an age of %d." % (self.name, self.age))
        elif self.age is not None:
            print("Your human already has an age of %d." % (self.age))
        else:
            self.age = human_age

    def hasBirthday(self, dob):
        """
        Name:     Human.hasBirthday
        Inputs:   str, birthday formatted as YYYY-MM-DD (dob)
        Outputs:  None.
        Features: Give your human a birthday
        Depends:  string_to_date
        """
        if self.dob is not None and self.name is not None:
            print("%s already has a birthday on %s." % self.dob)
        elif self.dob is not None:
            print("Your human already has a birthday on %s." % self.dob)
        else:
            try:
                tmp = string_to_date(dob)
            except ValueError:
                # It's okay if the birthday doesn't work
                pass
            else:
                self.dob = tmp

    def talk(self):
        """
        Name:     Human.talk
        Inputs:   None.
        Outputs:  None.
        Features: Have your human speak.
        """
        out_str = "Hello, world!\n"
        if self.name is not None:
            out_str += "My name is '%s'.\n" % (self.name)
        if self.age is not None:
            out_str += "I'm %d years old.\n" % (self.age)
        if self.dob is not None:
            today = datetime.date.today()
            today_month = today.month
            if self.dob.month == today.month and self.dob.day == today.day:
                out_str += "Today is my birthday!"
            else:
                out_str += "Today is not my birthday."
        else:
            out_str += "I don't have a birthday."
        print(out_str)

##############################################################################
# MAIN
##############################################################################
if __name__ == "__main__":
    # Initialize your class, set the class variables, and call talk():
    my_human = Human()
    my_human.hasName("The Duke")
    my_human.hasAge(100)
    my_human.hasBirthday("1999-02-17")
    my_human.talk()
