import React, { useState } from 'react';
import axios from 'axios';

const EventForm = ({ user }) => {
  const [formData, setFormData] = useState({ event_title: '', event_location: '', event_date: '', event_duration: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await axios.post('http://localhost:5000/add_event', { ...formData, organizer_id: user.user_id }, { withCredentials: true });
  };

  return (
    user.role === 'Organizer' && (
      <form onSubmit={handleSubmit}>
        <input name="event_title" onChange={handleChange} placeholder="Event Title" />
        <input name="event_location" onChange={handleChange} placeholder="Location" />
        <input name="event_date" onChange={handleChange} placeholder="Date" />
        <input name="event_duration" onChange={handleChange} placeholder="Duration" />
        <button type="submit">Create Event</button>
      </form>
    )
  );
};

export default EventForm;
