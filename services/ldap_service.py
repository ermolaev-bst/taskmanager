import ldap3
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, ANONYMOUS
from ldap3.core.exceptions import LDAPException
import logging
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

class LDAPService:
    """Сервис для интеграции с LDAP/Active Directory"""
    
    def __init__(self):
        self.connection = None
        self.server = None
        
    def test_connection(self, server_url: str, port: int, use_ssl: bool, 
                       bind_dn: str, bind_password: str, auth_method: str = 'SIMPLE') -> Dict:
        """Тестирование подключения к LDAP серверу"""
        try:
            # Создание сервера
            self.server = Server(server_url, port=port, use_ssl=use_ssl, get_info=ALL)
            
            # Настройка метода аутентификации
            if auth_method == 'NTLM':
                auth_mechanism = NTLM
            elif auth_method == 'ANONYMOUS':
                auth_mechanism = ANONYMOUS
            else:
                auth_mechanism = SIMPLE
            
            # Подключение
            self.connection = Connection(
                self.server,
                user=bind_dn,
                password=bind_password,
                authentication=auth_mechanism,
                auto_bind=True
            )
            
            if self.connection.bound:
                return {
                    'success': True,
                    'message': 'Подключение к LDAP серверу успешно установлено',
                    'server_info': str(self.server.info) if self.server.info else 'Информация недоступна'
                }
            else:
                return {
                    'success': False,
                    'message': 'Не удалось аутентифицироваться на LDAP сервере'
                }
                
        except LDAPException as e:
            logger.error(f"Ошибка LDAP: {str(e)}")
            return {
                'success': False,
                'message': f'Ошибка подключения к LDAP серверу: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {str(e)}")
            return {
                'success': False,
                'message': f'Неожиданная ошибка: {str(e)}'
            }
        finally:
            if self.connection:
                self.connection.unbind()
    
    def authenticate_user(self, username: str, password: str, 
                         server_url: str, port: int, use_ssl: bool,
                         bind_dn: str, bind_password: str, 
                         user_search_base: str, user_search_filter: str,
                         auth_method: str = 'SIMPLE') -> Dict:
        """Аутентификация пользователя через LDAP"""
        try:
            # Подключение к серверу
            self.server = Server(server_url, port=port, use_ssl=use_ssl, get_info=ALL)
            
            # Настройка метода аутентификации
            if auth_method == 'NTLM':
                auth_mechanism = NTLM
            elif auth_method == 'ANONYMOUS':
                auth_mechanism = ANONYMOUS
            else:
                auth_mechanism = SIMPLE
            
            # Подключение с правами администратора для поиска пользователей
            self.connection = Connection(
                self.server,
                user=bind_dn,
                password=bind_password,
                authentication=auth_mechanism,
                auto_bind=True
            )
            
            if not self.connection.bound:
                return {
                    'success': False,
                    'message': 'Не удалось подключиться к LDAP серверу'
                }
            
            # Поиск пользователя
            search_filter = user_search_filter.replace('{username}', username)
            self.connection.search(
                search_base=user_search_base,
                search_filter=search_filter,
                attributes=['cn', 'mail', 'department', 'title', 'memberOf', 'distinguishedName']
            )
            
            if not self.connection.entries:
                return {
                    'success': False,
                    'message': 'Пользователь не найден в LDAP'
                }
            
            user_entry = self.connection.entries[0]
            user_dn = user_entry.entry_dn
            
            # Попытка аутентификации пользователя
            user_connection = Connection(
                self.server,
                user=user_dn,
                password=password,
                authentication=auth_mechanism,
                auto_bind=True
            )
            
            if user_connection.bound:
                # Получение информации о пользователе
                user_info = {
                    'username': username,
                    'cn': str(user_entry.cn[0]) if user_entry.cn else username,
                    'email': str(user_entry.mail[0]) if user_entry.mail else '',
                    'department': str(user_entry.department[0]) if user_entry.department else '',
                    'title': str(user_entry.title[0]) if user_entry.title else '',
                    'groups': [str(group) for group in user_entry.memberOf] if user_entry.memberOf else [],
                    'dn': str(user_entry.distinguishedName[0]) if user_entry.distinguishedName else user_dn
                }
                
                user_connection.unbind()
                self.connection.unbind()
                
                return {
                    'success': True,
                    'message': 'Аутентификация успешна',
                    'user_info': user_info
                }
            else:
                self.connection.unbind()
                return {
                    'success': False,
                    'message': 'Неверный пароль пользователя'
                }
                
        except LDAPException as e:
            logger.error(f"Ошибка LDAP при аутентификации: {str(e)}")
            return {
                'success': False,
                'message': f'Ошибка LDAP: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при аутентификации: {str(e)}")
            return {
                'success': False,
                'message': f'Неожиданная ошибка: {str(e)}'
            }
        finally:
            if self.connection and self.connection.bound:
                self.connection.unbind()
    
    def search_users(self, search_term: str, server_url: str, port: int, use_ssl: bool,
                    bind_dn: str, bind_password: str, user_search_base: str,
                    auth_method: str = 'SIMPLE') -> Dict:
        """Поиск пользователей в LDAP"""
        try:
            # Подключение к серверу
            self.server = Server(server_url, port=port, use_ssl=use_ssl, get_info=ALL)
            
            # Настройка метода аутентификации
            if auth_method == 'NTLM':
                auth_mechanism = NTLM
            elif auth_method == 'ANONYMOUS':
                auth_mechanism = ANONYMOUS
            else:
                auth_mechanism = SIMPLE
            
            self.connection = Connection(
                self.server,
                user=bind_dn,
                password=bind_password,
                authentication=auth_mechanism,
                auto_bind=True
            )
            
            if not self.connection.bound:
                return {
                    'success': False,
                    'message': 'Не удалось подключиться к LDAP серверу'
                }
            
            # Поиск пользователей
            search_filter = f"(&(objectClass=person)(|(cn=*{search_term}*)(mail=*{search_term}*)(sAMAccountName=*{search_term}*)))"
            self.connection.search(
                search_base=user_search_base,
                search_filter=search_filter,
                attributes=['cn', 'mail', 'department', 'title', 'sAMAccountName', 'distinguishedName'],
                size_limit=50
            )
            
            users = []
            for entry in self.connection.entries:
                user_info = {
                    'cn': str(entry.cn[0]) if entry.cn else '',
                    'email': str(entry.mail[0]) if entry.mail else '',
                    'department': str(entry.department[0]) if entry.department else '',
                    'title': str(entry.title[0]) if entry.title else '',
                    'username': str(entry.sAMAccountName[0]) if entry.sAMAccountName else '',
                    'dn': str(entry.distinguishedName[0]) if entry.distinguishedName else ''
                }
                users.append(user_info)
            
            self.connection.unbind()
            
            return {
                'success': True,
                'message': f'Найдено пользователей: {len(users)}',
                'users': users
            }
            
        except LDAPException as e:
            logger.error(f"Ошибка LDAP при поиске: {str(e)}")
            return {
                'success': False,
                'message': f'Ошибка LDAP: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при поиске: {str(e)}")
            return {
                'success': False,
                'message': f'Неожиданная ошибка: {str(e)}'
            }
        finally:
            if self.connection and self.connection.bound:
                self.connection.unbind()
    
    def get_server_info(self, server_url: str, port: int, use_ssl: bool) -> Dict:
        """Получение информации о LDAP сервере"""
        try:
            self.server = Server(server_url, port=port, use_ssl=use_ssl, get_info=ALL)
            
            if self.server.info:
                return {
                    'success': True,
                    'server_info': {
                        'vendor_name': self.server.info.vendor_name,
                        'vendor_version': self.server.info.vendor_version,
                        'other': self.server.info.other,
                        'naming_contexts': self.server.info.naming_contexts,
                        'supported_controls': self.server.info.supported_controls,
                        'supported_extensions': self.server.info.supported_extensions,
                        'supported_sasl_mechanisms': self.server.info.supported_sasl_mechanisms
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Не удалось получить информацию о сервере'
                }
                
        except Exception as e:
            logger.error(f"Ошибка при получении информации о сервере: {str(e)}")
            return {
                'success': False,
                'message': f'Ошибка: {str(e)}'
            }
