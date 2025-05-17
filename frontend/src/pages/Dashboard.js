import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getRecommendedJobs } from '../services/jobService';
import JobList from '../components/job/JobList';
import ProfileSummary from '../components/profile/ProfileSummary';
import SkillsWidget from '../components/profile/SkillsWidget';
import './Dashboard.css';

const Dashboard = () => {
  const { currentUser } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const data = await getRecommendedJobs();
        setRecommendations(data.recommendations);
      } catch (err) {
        setError('Failed to fetch job recommendations');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  if (loading) {
    return <div className="loading">Loading your personalized dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Welcome, {currentUser.first_name}!</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-main">
          <div className="section">
            <h2>Recommended Jobs For You</h2>
            {error && <div className="error">{error}</div>}
            {recommendations.length > 0 ? (
              <JobList jobs={recommendations} />
            ) : (
              <p>
                We need more information about your skills and experience to 
                recommend jobs. Please update your profile to get personalized recommendations.
              </p>
            )}
          </div>
        </div>
        
        <div className="dashboard-sidebar">
          <ProfileSummary />
          <SkillsWidget />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;