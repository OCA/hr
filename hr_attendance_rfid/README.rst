.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
HR Attendance RFID
==================

This module extends the functionality of HR Attendance in order to allow
the logging of employee attendances using an RFID based employee
attendance system.

Configuration
=============

To use this module, you need to use an external system that calls the method
'register_attendance' of the model 'hr.employee' passing as parameter the
code of the RFID card.

Developers of a compatible RFID based employee attendance system should
be familiar with the outputs of this method and implement proper calls and
management of responses.

It is advisory to create an exclusive user to perform this task. As
user doesn't need several access, it is just essential to perform the check
in/out, a group has been created. Add your attendance device user to
RFID Attendance group.

Usage
=====

#. The HR employee responsible to set up new employees should go to
   'Attendances -> Manage Attendances -> Employees' and register the
   RFID card code of each of your employees. You can use an USB plugged
   RFID reader connected to your computer for this purpose.
#. The employee should put his/her card to the RFID based employee
   attendance system. It is expected that the system will provide some form
   of output of the registration event.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Omar Catiñeira Saavedra <omar@comunitea.com>
* Héctor Villarreal Ortega <hector.villarreal@eficent.com>
* Jordi Ballester Alomar <jordi.ballester@eficent.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
