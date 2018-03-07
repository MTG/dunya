import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { DATA_FETCH_STATUS } from 'constants';
import CategoryFilter from '../CategoryFilter';
import { getFiltersData } from '../../actions/filtersData';
import { toggleSelectedEntry } from '../../actions/filtersData';
import './RefineSearch.scss';

const sortCategories = (catA, catB) => {
  if (catA < catB) {
    return -1;
  }
  if (catB < catA) {
    return 1;
  }
  return 0;
};

const propTypes = {
  receivedData: PropTypes.object,
  status: PropTypes.string,
  getFiltersData: PropTypes.func,
  toggleSelectedEntry: PropTypes.func,
};

const renderRefineSection = (receivedData) => {
  const categories = Object.keys(receivedData);
  const sortedCategories = categories.sort(sortCategories);
  return (
    <div className="RefineSeach">
      <header className="RefineSearch__category-name-header">
        Filters
      </header>
      <nav>
        <ul className="RefineSearch__categories-list">
          {sortedCategories.map(category =>
            <CategoryFilter
              key={category}
              category={category}
              data={receivedData[category]}
            />)
          }
        </ul>
      </nav>
    </div>
  );
};

const renderProgressOverview = () =>
  <h2>Getting data...</h2>;

const renderErrorOverview = () =>
  <h2>There was an error retrieving data</h2>;


class RefineSearch extends React.Component {
  componentWillMount() {
    if (this.props.status !== DATA_FETCH_STATUS.SUCCESS) {
      // retrieve data to fill up the "refine" section (if not already fetched)
      this.props.getFiltersData();
    }else{
      var props = this.props;
      location.search.substr(1).split("&").forEach(function (item) {
        var tmp = item.split("=");
        props.toggleSelectedEntry(tmp[1], tmp[0]);
      }); 
    }
  }

  render() {
    const { receivedData, status,  } = this.props;
    switch (status) {
      case DATA_FETCH_STATUS.SUCCESS:
        return renderRefineSection(receivedData);
      case DATA_FETCH_STATUS.FAILURE:
        return renderErrorOverview();
      default:
        return renderProgressOverview();
    }
  }
}

const mapStateToProps = state => state.filtersData;

RefineSearch.propTypes = propTypes;

export default connect(mapStateToProps, { getFiltersData, toggleSelectedEntry })(RefineSearch);
