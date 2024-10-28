import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EventDetail = ({ event, user, fetchEvents }) => {
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [hasJoined, setHasJoined] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchJoinStatus = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/check_join_status/${event.event_id}`, {
          withCredentials: true,
        });
        setHasJoined(response.data.joined);
      } catch (error) {
        console.error("Error fetching join status:", error);
      }
    };

    fetchJoinStatus();
  }, [event.event_id]);

  const handleJoin = async () => {
    setLoading(true);
    try {
      await axios.post(`http://localhost:5000/join_event/${event.event_id}`, {}, { withCredentials: true });
      setFeedbackMessage("You have successfully joined the event.");
      setHasJoined(true);
      fetchEvents();
    } catch (error) {
      console.error("Error joining event:", error);
      setFeedbackMessage("An error occurred while trying to join the event.");
    }
    setLoading(false);
  };

  const handleLeave = async () => {
    setLoading(true);
    try {
      await axios.post(`http://localhost:5000/leave_event/${event.event_id}`, {}, { withCredentials: true });
      setFeedbackMessage("You have successfully left the event.");
      setHasJoined(false);
      fetchEvents();
    } catch (error) {
      console.error("Error leaving event:", error);
      setFeedbackMessage("An error occurred while trying to leave the event.");
    }
    setLoading(false);
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await axios.delete(`http://localhost:5000/cancel_event/${event.event_id}`, { withCredentials: true });
      setFeedbackMessage("The event has been deleted.");
      fetchEvents();
    } catch (error) {
      console.error("Error deleting event:", error);
      setFeedbackMessage("An error occurred while trying to delete the event.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (feedbackMessage) {
      const timer = setTimeout(() => setFeedbackMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [feedbackMessage]);

  return (
    <div>
      <h3>{event.event_title}</h3>
      <p>{event.event_location}</p>
      <p>{new Date(event.event_date).toLocaleString()}</p>
      <p>{event.event_duration}</p>
      {user && (
        <div>
          {user.role === 'Joiner' ? (
            <>
              {!hasJoined ? (
                <button onClick={handleJoin} disabled={loading}>Join</button>
              ) : (
                <button onClick={handleLeave} disabled={loading}>Leave</button>
              )}
            </>
          ) : user.role === 'Organizer' && event.organizer_id === user.user_id ? (
            <button onClick={handleDelete} disabled={loading}>Delete Event</button>
          ) : null}
        </div>
      )}
      {feedbackMessage && <p>{feedbackMessage}</p>}
    </div>
  );
};

export default EventDetail;
