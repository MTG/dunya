import PropTypes from 'prop-types';
import React from 'react';
import { USE_REMOTE_SOURCES, REMOTE_URL } from 'settings';
import './ResultItem.scss';

const propTypes = {
  collaborators: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    instrument: PropTypes.string,
  })),
  concert: PropTypes.string,
  image: PropTypes.string,
  linkToRecording: PropTypes.string,
  mainArtists: PropTypes.arrayOf(PropTypes.string),
  name: PropTypes.string,
  selectedArtists: PropTypes.array,
};

const renderList = list => list.join(', ');

const renderCollaboratorsFacts = (selectedArtists = [], recordingArtists = []) => {
  const facts = recordingArtists.reduce((curFacts, curArtist) => {
    if (selectedArtists.includes(curArtist.name)) {
      const instrumentPlayed = curArtist.instrument;
      const factVerb = (instrumentPlayed === 'voice') ?
        'sings' : `plays the ${instrumentPlayed}`;
      const curArtistFact =
        <span><span className="fact__artist">{curArtist.name}</span> {factVerb}</span>;
      return [...curFacts, curArtistFact];
    }
    return curFacts;
  }, []);
  return (
    <ul className="ResultItem__collaborators_facts">
      {facts.map((fact, index) => <li key={index}>{fact}</li>)}
    </ul>
  );
};

const ResultItem = (props) => {
  let imageSrc = props.image;
  let { linkToRecording } = props;
  if (USE_REMOTE_SOURCES) {
    imageSrc = REMOTE_URL + imageSrc;
    linkToRecording = REMOTE_URL + linkToRecording;
  }
  const mainKeys = Object.keys(propTypes);
  // other keys such as taala, raaga, form, ...
  const otherInfoKeys = Object.keys(props).filter(key => !mainKeys.includes(key));
  return (
    <a href={linkToRecording} className="ResultItem">
      <div className="ResultItem__header">
        <img src={imageSrc} alt="concert artwork" className="ResultItem__concert-artwork" />
        <div className="ResultItem__main-info">
          <div className="ResultItem__name">
            {props.name}
          </div>
          <div className="ResultItem__concert">
            {props.concert}
          </div>
          <div className="ResultItem__main-artists">
            {renderList(props.mainArtists)}
          </div>
        </div>
      </div>
      <div className="ResultItem__details">
        <div className="ResultItem__collaborators">
          {renderCollaboratorsFacts(props.selectedArtists, props.collaborators)}
        </div>
        <div className="ResultItem__other-info__container">
          {otherInfoKeys.map(section =>
            <div className="ResultItem__other-info" key={section}>
              <div className="ResultItem__details__header">{section}</div>
              <div className="ResultItem__other-info-list">
                {renderList(props[section])}
              </div>
            </div>
          )}
        </div>
      </div>
    </a>
  );
};

ResultItem.propTypes = propTypes;
export default ResultItem;
