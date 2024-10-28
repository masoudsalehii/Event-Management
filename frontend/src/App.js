import './styles.css';
import React, { useState, useEffect } from 'react';
import Auth from './components/Auth';
import EventsList from './components/EventsList';
import EventDetail from './components/EventDetail';
import EventForm from './components/EventForm';
import { io } from 'socket.io-client';
import axios from 'axios';
import JoinersList from './components/JoinersList';

const socket = io('http://localhost:5000');

const App = () => {
  const [user, setUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);

  const fetchEvents = async () => {
    try {
      const response = await axios.get('http://localhost:5000/events', { withCredentials: true });
      setEvents(response.data);
      if (selectedEvent && !response.data.some(event => event.event_id === selectedEvent.event_id)) {
        setSelectedEvent(null);
      }
    } catch (error) {
      console.error("Error fetching events:", error);
    }
  };

  useEffect(() => {
    if (user) {
      fetchEvents();
    }
    socket.on('event_added', fetchEvents);
    socket.on('event_canceled', fetchEvents);

    return () => {
      socket.off('event_added', fetchEvents);
      socket.off('event_canceled', fetchEvents);
    };
  }, [user]);

  const handleEventSelect = (event) => {
    setSelectedEvent(event);
  };

  const handleLogout = () => {
    setUser(null);
    setEvents([]);
    setSelectedEvent(null);
  };

  return (
    <div className="app-container">
      {!user ? (
        <Auth setUser={setUser} />
      ) : (
        <>
          <header className="header">
            <h1>Welcome, {user.name}</h1>
            <button onClick={handleLogout}>Logout</button>
          </header>

          <div className="content">
            {/* Left Sidebar: Event Creation Form for Organizers */}
            <div className="sidebar-left">
              {user.role === 'Organizer' && (
                <EventForm user={user} fetchEvents={fetchEvents} />
              )}
            </div>

            {/* Center: Events List */}
            <div className="events-list">
              <EventsList events={events} setSelectedEvent={handleEventSelect} />
            </div>

            {/* Right Sidebar: Event Details */}
            <div className="sidebar-right">
              {selectedEvent && (
                <>
                <EventDetail event={selectedEvent} user={user} fetchEvents={fetchEvents} />
                <JoinersList event={selectedEvent} />
                </>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default App;
