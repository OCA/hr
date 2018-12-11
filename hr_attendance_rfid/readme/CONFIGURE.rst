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
