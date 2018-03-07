import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import { updateWindowSize } from 'actions/windowSize';

const propTypes = {
  updateWindowSize: PropTypes.func,
};

class ResizeListener extends React.Component {
  constructor(props) {
    super(props);
    this.handleResize = this.handleResize.bind(this);
  }
  componentWillMount() {
    window.addEventListener('resize', this.handleResize);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.handleResize);
  }

  handleResize() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    this.props.updateWindowSize({ width, height });
  }

  render() {
    return null;
  }
}

ResizeListener.propTypes = propTypes;
export default connect(() => ({}), { updateWindowSize })(ResizeListener);
