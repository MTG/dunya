import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { makeGetDetailsForCategorySelectedEntries } from '../../selectors/filtersData';
import ResultItem from './ResultItem';

const propTypes = {
  results: PropTypes.array,
  children: PropTypes.element,
  selectedArtists: PropTypes.array,
};

const Results = props => (
  <section className="Results">
    <header className="Results__header">
      Results
    </header>
    <div className="Results__list">
      {props.results.map((result, index) =>
        <ResultItem key={index} {...result} selectedArtists={props.selectedArtists} />)}
    </div>
    {props.children}
  </section>
);

const mapStateToProps = (state) => {
  const getDetailsForCategorySelectedEntries = makeGetDetailsForCategorySelectedEntries();
  const selectedArtistsDetails = getDetailsForCategorySelectedEntries(state, { category: 'artists' });
  return {
    selectedArtists: selectedArtistsDetails.map(artist => artist.name),
  };
};
Results.propTypes = propTypes;
export default connect(mapStateToProps, {})(Results);
