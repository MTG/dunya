import React from 'react';
import Search from '../Search';
import ResultsContainer from '../Results/ResultsContainer';
import './MainBody.scss';

const MainBody = () => (
  <div className="MainBody">
    <section className="MainBody__Item">
      <Search />
    </section>
    <section className="MainBody__Item">
      <ResultsContainer />
    </section>
  </div>
);

export default MainBody;
