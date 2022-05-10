import React from 'react';
import { LOGIN_URL, LOGOUT_URL, USER_PROFILE_BASE_URL } from '../../settings';

const buildLink = (name, link) => ({ link, name });

const getLinks = () => {
  const isUserLoggedIn = Boolean(window.username) && window.username !== '{% user_name %}';
  const contact = buildLink('Info', './info');
  const about = buildLink('Legal', 'https://dunya.compmusic.upf.edu/about/terms');
  const register = buildLink('Register', 'https://dunya.compmusic.upf.edu/user/register');
  const login = buildLink('Login', LOGIN_URL);
  const logout = buildLink('Logout', LOGOUT_URL);
  const user = buildLink(window.username, `${USER_PROFILE_BASE_URL}/${window.username}`);
  if (isUserLoggedIn) {
    return [contact, about, user, logout];
  }
  return [contact, about, register, login];
};

const NavLinks = () => (
    <nav className="NavLinks">
      <ul>
        {getLinks().map(link => (
            <li key={link.name}><a className="NavLinks__item" href={link.link}>{link.name}</a></li>
        ))}
      </ul>
    </nav>);

export default NavLinks;