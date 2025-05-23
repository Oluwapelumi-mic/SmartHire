import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import './ProfileCompleteness.css';

const ProfileCompleteness = ({ score, profile }) => {
  // Determine which sections need attention
  const getMissingItems = () => {
    const missing = [];
    
    if (!profile) return ['Create your profile to get started'];
    
    if (!profile.headline || profile.headline.trim() === '') 
      missing.push('Add a professional headline');
    
    if (!profile.summary || profile.summary.trim() === '') 
      missing.push('Write a summary about yourself');
    
    if (!profile.skills || profile.skills.length === 0)
      missing.push('Add your key skills');
    
    if (!profile.experiences || profile.experiences.length === 0)
      missing.push('Add work experience');
    
    if (!profile.education || profile.education.trim() === '')
      missing.push('Add education details');
    
    return missing.length ? missing : ['Your profile is complete!'];
  };
  
  const missingItems = getMissingItems();
  
  // Determine color based on score
  const getColor = () => {
    if (score >= 80) return '#4CAF50'; // Green
    if (score >= 50) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };
  
  return (
    <section className="dashboard-section profile-completeness">
      <h3>Profile Completeness</h3>
      
      <div className="progress-container">
        <div className="progress-chart">
          <CircularProgressbar
            value={score}
            text={`${score}%`}
            styles={buildStyles({
              textSize: '24px',
              pathColor: getColor(),
              textColor: '#333333',
              trailColor: '#e0e0e0',
            })}
          />
        </div>
        
        <div className="progress-details">
          <ul className="missing-items">
            {missingItems.map((item, index) => (
              <li key={index}>
                {item !== 'Your profile is complete!' ? (
                  <span className="todo-item">⚠️ {item}</span>
                ) : (
                  <span className="complete-item">✅ {item}</span>
                )}
              </li>
            ))}
          </ul>
          
          <a href="/profile" className="profile-action-button">
            {score < 100 ? 'Complete Your Profile' : 'View Your Profile'}
          </a>
        </div>
      </div>
    </section>
  );
};

export default ProfileCompleteness;