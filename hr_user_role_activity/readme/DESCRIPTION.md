Glue module between `base_user_role_activity` and `hr`.

When a user role assignment is about to expire, the reminder activity is
assigned to the manager of the related employee instead of the user itself.
When the user has no employee record with a manager, the activity stays
assigned to the user.