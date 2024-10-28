import React from 'react';
import '../styles.css';

const EventsList = ({ events, setSelectedEvent }) => {
  return (
    <div className="events-list">
      <h2>Events</h2>
      <ul className="event-items">
        {events.map((event) => (
          <li
            key={event.event_id}
            className="event-item"
            onClick={() => setSelectedEvent(event)}
          >
            <span className="event-title">{event.event_title}</span>
            <span className="event-location">{event.event_location}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EventsList;
