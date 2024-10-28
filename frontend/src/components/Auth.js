import '../styles.css';
import React, { useState } from 'react';
import axios from 'axios';

const Auth = ({ setUser }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    password: '',
    role: 'Joiner'
  });

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleAuth = async (e) => {
    e.preventDefault();

    try {
      if (isLogin) {
        const response = await axios.post(
          'http://localhost:5000/login',
          {
            name: formData.name,
            password: formData.password
          },
          { withCredentials: true }
        );
        setUser(response.data.user); 
        alert(`Welcome back, ${response.data.user.name}!`);
      } else {
        const response = await axios.post(
          'http://localhost:5000/register',
          {
            name: formData.name,
            role: formData.role,
            password: formData.password
          }
        );
        alert('Registration successful! Please log in.');
        setIsLogin(true); 
        setFormData({ ...formData, user_id: response.data.user_id });
      }
    } catch (error) {
      console.error(error.response?.data || error.message);
      alert(error.response?.data?.error || 'Authentication failed');
    }
  };

  return (
    <div className="auth-container">
      <h2>{isLogin ? 'Login' : 'Register'}</h2>
      <form onSubmit={handleAuth}>
        {isLogin ? (
          <>
            <input
              type="text"
              name="name"
              onChange={handleInputChange}
              placeholder="Username"
              value={formData.name}
              required
            />
            <input
              type="password"
              name="password"
              onChange={handleInputChange}
              placeholder="Password"
              value={formData.password}
              required
            />
          </>
        ) : (
          <>
            <input
              type="text"
              name="name"
              onChange={handleInputChange}
              placeholder="Name"
              value={formData.name}
              required
            />
            <select name="role" onChange={handleInputChange} value={formData.role}>
              <option value="Joiner">Joiner</option>
              <option value="Organizer">Organizer</option>
            </select>
            <input
              type="password"
              name="password"
              onChange={handleInputChange}
              placeholder="Password"
              value={formData.password}
              required
            />
          </>
        )}
        <button type="submit">{isLogin ? 'Login' : 'Register'}</button>
      </form>
      
      {isLogin ? (
        <p>
          Don't have an account?{' '}
          <button onClick={() => setIsLogin(false)}>Register</button>
        </p>
      ) : (
        <p>
          Do you already have an account?{' '}
        <button onClick={() => setIsLogin(true)}>Login</button>
        </p>
      )}
    </div>
  );
};

export default Auth;
