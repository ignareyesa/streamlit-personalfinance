import jwt
import bcrypt
import streamlit as st
from datetime import datetime, timedelta
import extra_streamlit_components as stx

from .hasher import Hasher
from .utils import generate_random_pw, check_email

from .exceptions import CredentialsError, ResetError, RegisterError, ForgotError, UpdateError, UsernameError

class Authenticate:
    """
    This class will create login, logout, register user, reset password, forgot password, 
    forgot username, and modify user details widgets.
    """
    def __init__(self, credentials: dict, cookie_name: str, key: str, cookie_expiry_days: int=30, 
        preauthorized: list=None):
        """
        Create a new instance of "Authenticate".

        Parameters
        ----------
        credentials: dict
            The dictionary of usernames, names, passwords, and emails.
        cookie_name: str
            The name of the JWT cookie stored on the client's browser for passwordless reauthentication.
        key: str
            The key to be used for hashing the signature of the JWT cookie.
        cookie_expiry_days: int
            The number of days before the cookie expires on the client's browser.
        preauthorized: list
            The list of emails of unregistered users authorized to register.
        """
        self.credentials = credentials
        self.credentials['usernames'] = {key.lower(): value for key, value in credentials['usernames'].items()}
        self.cookie_name = cookie_name
        self.key = key
        self.cookie_expiry_days = cookie_expiry_days
        self.preauthorized = preauthorized
        self.cookie_manager = stx.CookieManager()

        if 'name' not in st.session_state:
            st.session_state['name'] = None
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None
        if 'username' not in st.session_state:
            st.session_state['username'] = None
        if 'logout' not in st.session_state:
            st.session_state['logout'] = None

    def _token_encode(self) -> str:
        """
        Encodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The JWT cookie for passwordless reauthentication.
        """
        return jwt.encode({'name':st.session_state['name'],
            'username':st.session_state['username'],
            'exp_date':self.exp_date}, self.key, algorithm='HS256')

    def _token_decode(self) -> str:
        """
        Decodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The decoded JWT cookie for passwordless reauthentication.
        """
        try:
            return jwt.decode(self.token, self.key, algorithms=['HS256'])
        except:
            return False

    def _set_exp_date(self) -> str:
        """
        Creates the reauthentication cookie's expiry date.

        Returns
        -------
        str
            The JWT cookie's expiry timestamp in Unix epoch.
        """
        return (datetime.utcnow() + timedelta(days=self.cookie_expiry_days)).timestamp()

    def _check_pw(self) -> bool:
        """
        Checks the validity of the entered password.

        Returns
        -------
        bool
            The validity of the entered password by comparing it to the hashed password on disk.
        """
        return bcrypt.checkpw(self.password.encode(), 
            self.credentials['usernames'][self.username]['password'].encode())

    def _check_cookie(self):
        """
        Checks the validity of the reauthentication cookie.
        """
        self.token = self.cookie_manager.get(self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if self.token is not False:
                if not st.session_state['logout']:
                    if self.token['exp_date'] > datetime.utcnow().timestamp():
                        if 'name' and 'username' in self.token:
                            st.session_state['name'] = self.token['name']
                            st.session_state['username'] = self.token['username']
                            st.session_state['authentication_status'] = True
    
    def _check_credentials(self, inplace: bool=True) -> bool:
        """
        Checks the validity of the entered credentials.

        Parameters
        ----------
        inplace: bool
            Inplace setting, True: authentication status will be stored in session state, 
            False: authentication status will be returned as bool.
        Returns
        -------
        bool
            Validity of entered credentials.
        """
        if self.username in self.credentials['usernames']:
            try:
                if self._check_pw():
                    if inplace:
                        st.session_state['name'] = self.credentials['usernames'][self.username]['name']
                        self.exp_date = self._set_exp_date()
                        self.token = self._token_encode()
                        self.cookie_manager.set(self.cookie_name, self.token,
                            expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days))
                        st.session_state['authentication_status'] = True
                    else:
                        return True
                else:
                    if inplace:
                        st.session_state['authentication_status'] = False
                    else:
                        return False
            except Exception as e:
                print(e)
        else:
            if inplace:
                st.session_state['authentication_status'] = False
            else:
                return False
    
    def _check_username(self) -> bool :
        """
        Checks the validity of the entered username.

        Parameters
        ----------
        Returns
        -------
        bool
            Validity of entered credentials.
        """
        if self.username in self.credentials['usernames']:
            return True
        else:
            return False


    def login(self, form_name: str, location: str='main') -> tuple:
        """
        Creates a login widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the login form.
        location: str
            The location of the login form i.e. main or sidebar.
        Returns
        -------
        str
            Name of the authenticated user.
        bool
            The status of authentication, None: no credentials entered, 
            False: incorrect credentials, True: correct credentials.
        str
            Username of the authenticated user.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if (not st.session_state['authentication_status']) or (not "authentication_status" in st.session_state):
            self._check_cookie()
            if st.session_state['authentication_status'] != True:
                if location == 'main':
                    login_form = st.form('Login')
                elif location == 'sidebar':
                    login_form = st.sidebar.form('Login')

                login_form.subheader(form_name)
                self.username = login_form.text_input('Nombre de usuario').lower()
                st.session_state['username'] = self.username
                self.password = login_form.text_input('Contreseña', type='password')

                if login_form.form_submit_button('Iniciar sesión'):
                    self._check_credentials()

        return st.session_state['name'], st.session_state['authentication_status'], st.session_state['username']

    def logout(self, button_name: str, location: str='main'):
        """
        Creates a logout button.

        Parameters
        ----------
        button_name: str
            The rendered name of the logout button.
        location: str
            The location of the logout button i.e. main or sidebar.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            if st.button(button_name):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state['logout'] = True
                st.session_state['name'] = None
                st.session_state['username'] = None
                st.session_state['authentication_status'] = None
        elif location == 'sidebar':
            if st.sidebar.button(button_name):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state['logout'] = True
                st.session_state['name'] = None
                st.session_state['username'] = None
                st.session_state['authentication_status'] = None

    def username_form(self, form_name: str, location: str='main') -> str:
        """
        Create a username checker widget
        
        Parameters
        ----------
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        Returns
        -------
        str
            username if it is valid.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            check_username_form = st.form('Reset password')
        elif location == 'sidebar':
            check_username_form = st.sidebar.form('Reset password')
        
        check_username_form.subheader(form_name)
        self.username = check_username_form.text_input('Nombre de usuario').lower()

        if check_username_form.form_submit_button('Enviar'):
            if len(self.username) > 0:
                if self._check_username():
                    return self.username
                else:
                    raise UsernameError
            else: raise ResetError("No se ha proporcionado un nombre de usuario")


    def _update_password(self, username: str, password: str):
        """
        Updates credentials dictionary with user's reset hashed password.

        Parameters
        ----------
        username: str
            The username of the user to update the password for.
        password: str
            The updated plain text password.
        """
        self.credentials['usernames'][username]['password'] = Hasher([password]).generate()[0]

    def reset_password(self, username: str, form_name: str, location: str='main') -> bool:
        """
        Creates a password reset widget.

        Parameters
        ----------
        username: str
            The username of the user to reset the password for.
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        Returns
        -------
        str
            The status of resetting the password.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            reset_password_form = st.form('Reset password')
        elif location == 'sidebar':
            reset_password_form = st.sidebar.form('Reset password')
        
        reset_password_form.subheader(form_name)
        self.username = username.lower()
        self.password = reset_password_form.text_input('Contraseña actual', type='password')
        new_password = reset_password_form.text_input('Nueva contraseña', type='password')
        new_password_repeat = reset_password_form.text_input('Repetir contreseña', type='password')

        if reset_password_form.form_submit_button('Cambiar contreseña'):
            if self._check_credentials(inplace=False):
                if len(new_password) > 0:
                    if new_password == new_password_repeat:
                        if self.password != new_password: 
                            self._update_password(self.username, new_password)
                            return True
                        else:
                            raise ResetError('La contraseña actual y la nueva son las mismas')
                    else:
                        raise ResetError('Las contraseñas no coinciden')
                else:
                    raise ResetError('No se ha proporcionado una contraseña')
            else:
                raise CredentialsError
    
    def _register_credentials(self, username: str, name: str, password: str, email: str, preauthorization: bool):
        """
        Adds to credentials dictionary the new user's information.

        Parameters
        ----------
        username: str
            The username of the new user.
        name: str
            The name of the new user.
        password: str
            The password of the new user.
        email: str
            The email of the new user.
        preauthorization: bool
            The pre-authorization requirement, True: user must be pre-authorized to register, 
            False: any user can register.
        """
        self.credentials['usernames'][username] = {'name': name, 
            'password': Hasher([password]).generate()[0], 'email': email}
        if preauthorization:
            self.preauthorized['emails'].remove(email)

    def register_user(self, form_name: str, location: str='main', preauthorization=True) -> bool:
        """
        Creates a password reset widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        preauthorization: bool
            The pre-authorization requirement, True: user must be pre-authorized to register, 
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if not self.preauthorized:
            raise ValueError("Pre-authorization argument must not be None")
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            register_user_form = st.form('Register user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')

        register_user_form.subheader(form_name)
        new_email = register_user_form.text_input('Email')
        new_username = register_user_form.text_input('Nombre de usuario').lower()
        new_name = register_user_form.text_input('Nombre')
        new_password = register_user_form.text_input('Contreseña', type='password')
        new_password_repeat = register_user_form.text_input('Repetir contraseña', type='password')

        if register_user_form.form_submit_button('Registrarse'):
            if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                if check_email(new_email):
                    if new_username not in self.credentials['usernames']:
                        if new_password == new_password_repeat:
                            if preauthorization:
                                if new_email in self.preauthorized['emails']:
                                    self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                                    return True
                                else:
                                    raise RegisterError('User not pre-authorized to register')
                            else:
                                self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                                return True
                        else:
                            raise RegisterError('Las contraseñas no coinciden')
                    else:
                        raise RegisterError('El nombre de usuario ya existe')
                else:
                    raise RegisterError('El email introducido no es válido')
            else:
                raise RegisterError('Porfavor rellene todos los valores del formulario')

    def _set_random_password(self, username: str) -> str:
        """
        Updates credentials dictionary with user's hashed random password.

        Parameters
        ----------
        username: str
            Username of user to set random password for.
        Returns
        -------
        str
            New plain text password that should be transferred to user securely.
        """
        self.random_password = generate_random_pw()
        self.credentials['usernames'][username]['password'] = Hasher([self.random_password]).generate()[0]
        return self.random_password

    def forgot_password(self, username: str, form_name: str, location: str='main') -> bool:
        """
        Creates a forgot password widget.

        Parameters
        ----------
        username:str
            The username of the user who has forgot the password
        form_name: str
            The rendered name of the forgot username form.
        location: str
            The location of the forgot username form i.e. main or sidebar.
        Returns
        -------
        bool
            The status of registering the new password, True: new password updated successfully.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            reset_password_form = st.form('Reset password Link')
        elif location == 'sidebar':
            reset_password_form = st.sidebar.form('Reset password Link')
        
        reset_password_form.subheader(form_name)
        self.username = username.lower()
        new_password = reset_password_form.text_input('Nueva contraseña', type='password')
        new_password_repeat = reset_password_form.text_input('Repetir contreseña', type='password')

        if reset_password_form.form_submit_button('Cambiar contreseña'):
            if self._check_username():
                if len(new_password) > 0:
                    if new_password == new_password_repeat:
                        if self.password != new_password: 
                            self._update_password(self.username, new_password)
                            return True
                        else:
                            raise ResetError('La contraseña actual y la nueva son las mismas')
                    else:
                        raise ResetError('Las contraseñas no coinciden')
                else:
                    raise ResetError('No se ha proporcionado una contraseña')
            else:
                raise UsernameError

    def _get_username(self, key: str, value: str) -> str:
        """
        Retrieves username based on a provided entry.

        Parameters
        ----------
        key: str
            Name of the credential to query i.e. "email".
        value: str
            Value of the queried credential i.e. "jsmith@gmail.com".
        Returns
        -------
        str
            Username associated with given key, value pair i.e. "jsmith".
        """
        for username, entries in self.credentials['usernames'].items():
            if entries[key] == value:
                return username
        return False

    def forgot_username(self, form_name: str, location: str='main') -> tuple:
        """
        Creates a forgot username widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the forgot username form.
        location: str
            The location of the forgot username form i.e. main or sidebar.
        Returns
        -------
        str
            Forgotten username that should be transferred to user securely.
        str
            Email associated with forgotten username.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            forgot_username_form = st.form('Forgot username')
        elif location == 'sidebar':
            forgot_username_form = st.sidebar.form('Forgot username')

        forgot_username_form.subheader(form_name)
        email = forgot_username_form.text_input('Email')

        if forgot_username_form.form_submit_button('Enviar'):
            if len(email) > 0 or check_email(email):
                return self._get_username('email', email), email
            else:
                raise ForgotError('Introduzca un email válido.')
        return None, email

    def _update_entry(self, username: str, key: str, value: str):
        """
        Updates credentials dictionary with user's updated entry.

        Parameters
        ----------
        username: str
            The username of the user to update the entry for.
        key: str
            The updated entry key i.e. "email".
        value: str
            The updated entry value i.e. "jsmith@gmail.com".
        """
        self.credentials['usernames'][username][key] = value

    def update_user_details(self, username: str, form_name: str, location: str='main') -> bool:
        """
        Creates a update user details widget.

        Parameters
        ----------
        username: str
            The username of the user to update user details for.
        form_name: str
            The rendered name of the update user details form.
        location: str
            The location of the update user details form i.e. main or sidebar.
        Returns
        -------
        str
            The status of updating user details.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            update_user_details_form = st.form('Update user details')
        elif location == 'sidebar':
            update_user_details_form = st.sidebar.form('Update user details')
        
        update_user_details_form.subheader(form_name)
        self.username = username.lower()
        field = update_user_details_form.selectbox('Dato', ['Nombre', 'Email']).lower()
        field = field.replace("nombre","name")
        new_value = update_user_details_form.text_input('Nuevo valor')

        if update_user_details_form.form_submit_button('Enviar'):
            if len(new_value) > 0:
                if new_value != self.credentials['usernames'][self.username][field]:
                    if field == 'email':
                        if check_email(new_value):
                            self._update_entry(self.username, field, new_value)
                        else:
                            raise RegisterError("El email introducido no es válido")
                    if field == 'name':
                        self._update_entry(self.username, field, new_value)
                        st.session_state['name'] = new_value
                        # self.exp_date = self._set_exp_date()
                        # self.token = self._token_encode()
                        # self.cookie_manager.set(self.cookie_name, self.token,
                        # expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days))
                    return True
                else:
                    raise UpdateError('El valor nuevo y el antiguo son el mismo')
                    
            if len(new_value) == 0:
                raise UpdateError('No se ha introducido ningun valor')

    
    def _update_username(self, username: str, new_username: str):
        """
        Updates credentials dictionary with username updated entry.

        Parameters
        ----------
        username: str
            The username of the user to update the entry for.
        new_username: str
            The updated username.
        """
        self.credentials['usernames'][new_username] = self.credentials['usernames'][username]
        del self.credentials["usernames"][username]

    def reset_username(self, form_name: str, location: str='main') -> bool:
        """
        Creates a username reset widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        Returns
        -------
        str
            The new username.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            reset_username_form = st.form('Reset password')
        elif location == 'sidebar':
            reset_username_form = st.sidebar.form('Reset password')
        
        reset_username_form.subheader(form_name)
        self.username = reset_username_form.text_input('Nombre de usuario actual').lower()
        new_username = reset_username_form.text_input('Nuevo nombre de usuario').lower()
        self.password = reset_username_form.text_input('Contraseña', type='password')

        if reset_username_form.form_submit_button('Cambiar nombre de usuario'):
            if self._check_credentials(inplace=False):
                if len(new_username) > 0:
                    if self.username != new_username: 
                        self._update_username(self.username, new_username)
                        st.session_state['username'] = new_username
                        # self.exp_date = self._set_exp_date()
                        # self.token = self._token_encode()
                        # self.cookie_manager.set(self.cookie_name, self.token,
                        # expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days))
                        return new_username
                    else:
                        raise ResetError('El nombre de usuario actual y el nuevo son el mismo')
                else:
                    raise ResetError('No se ha proporcionado un nuevo nombre de usuario')
            else:
                raise CredentialsError