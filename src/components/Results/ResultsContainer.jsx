import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { DATA_FETCH_STATUS } from '../../constants';
import { getMoreResults } from '../../actions/search';
import LoadMoreResultsButton from './LoadMoreResultsButton';
import Results from './index';
import Loading from '../Loading';
import './Results.scss';

const propTypes = {
  status: PropTypes.string,
  results: PropTypes.array,
  moreResults: PropTypes.number,
  getMoreResults: PropTypes.func,
};

const ResultsContainer = (props) => {
  switch (props.status) {
    case (DATA_FETCH_STATUS.NOT_ASKED):
      return null;
    case (DATA_FETCH_STATUS.PROGRESS): {
      const progress = <Loading />;
      if (props.results.length) {
        return <Results results={props.results}>{progress}</Results>;
      }
      return progress;
    }
    case (DATA_FETCH_STATUS.SUCCESS): {
      let loadMoreButton = null;
      if (props.moreResults) {
        loadMoreButton = (
          <form
            onSubmit={(evt) => {
              evt.preventDefault();
              props.getMoreResults();
            }}
          >
            <LoadMoreResultsButton moreResults={props.moreResults} />
          </form>
        );
      }
      return <Results results={props.results}>{loadMoreButton}</Results>;
    }
    case (DATA_FETCH_STATUS.FAILURE): {
      return <div className="Results__fetch-errors">Errors while retrieving data</div>;
    }
    default:
      return null;
  }
};

ResultsContainer.propTypes = propTypes;

export default connect((state) => {
  const { status, results, moreResults } = state.search;
  return { status, results, moreResults };
}, { getMoreResults })(ResultsContainer);
