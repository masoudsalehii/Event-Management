import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client'; 
import '../styles.css';

const JoinersList = ({ event }) => {
  const [joiners, setJoiners] = useState([]);
  const [loading, setLoading] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');


  useEffect(() => {
    const socket = io('http://localhost:5000');

    const fetchJoiners = async () => {
      setLoading(true); 
      try {
        const response = await axios.get(
          `http://localhost:5000/events/${event.event_id}/joiners`,
          { withCredentials: true } 
        );
        setJoiners(response.data);
        setFeedbackMessage('Joiners fetched successfully.');
      } catch (error) {
        console.error("Error fetching joiners:", error);
        setFeedbackMessage("Failed to fetch joiners.");
      } finally {
        setLoading(false); 
      }
    };

    if (event) fetchJoiners(); 


    socket.on('joiner_joined', ({ event_id, name }) => {
      if (event.event_id === event_id) {
        setJoiners((prevJoiners) => [...prevJoiners, { user_id: Date.now(), name }]);
        setFeedbackMessage(`${name} joined the event.`);
      }
    });


    socket.on('joiner_left', ({ event_id }) => {
      if (event.event_id === event_id) {
        fetchJoiners(); 
      }
    });

 
    return () => {
      socket.off('joiner_joined');
      socket.off('joiner_left');
      socket.disconnect();
    };
  }, [event]);

  return (
    <div className="joiners-list">
      <h3>Joiners</h3>
      {loading ? (
        <p>Loading joiners...</p>
      ) : (
        <>
          <p>{feedbackMessage}</p>
          <ul>
            {joiners.length > 0 ? (
              joiners.map((joiner) => (
                <li key={joiner.user_id} className="joiner-item">
                  {joiner.name}
                </li>
              ))
            ) : (
              <li>No joiners for this event yet.</li>
            )}
          </ul>
        </>
      )}
    </div>
  );
};

export default JoinersList;
