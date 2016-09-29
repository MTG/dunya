import React from 'react';

const links = [
  {
    link: 'https://dunya.compmusic.upf.edu/about/contact',
    name: 'Contact',
  },
  {
    link: 'https://dunya.compmusic.upf.edu/about/terms',
    name: 'About',
  },
  {
    link: 'https://dunya.compmusic.upf.edu/social/register',
    name: 'Register',
  },
];

export default () => (
  <nav className="NavLinks">
    <ul>
      {links.map((link) => (
        <li key={link.name}><a className="NavLinks__item" href={link.link}>{link.name}</a></li>
      ))}
    </ul>
  </nav>);
