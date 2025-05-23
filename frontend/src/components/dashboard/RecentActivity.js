import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import './RecentActivity.css';

const RecentActivity = ({ applications }) => {
  // Get the 5 most recent activities (applications only for now)
  const recentActivities = applications
    .sort((a, b) => new Date(b.applied_at) - new Date(a.applied_at))
    .slice(0, 5);
  
  return (
    <section className="dashboard-section recent-activity">
      <h3>Recent Activity</h3>
      
      {recentActivities.length > 0 ? (
        <ul className="activity-list">
          {recentActivities.map((activity) => (
            <li key={activity.id} className="activity-item">
              <div className="activity-icon">
                <i className="fas fa-paper-plane"></i>
              </div>
              <div className="activity-content">
                <p className="activity-description">
                  Applied for <strong>{activity.job.title}</strong> at {activity.job.company}
                </p>
                <p className="activity-time">
                  {formatDistanceToNow(new Date(activity.applied_at), { addSuffix: true })}
                </p>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <div className="empty-activity">
          <p>No recent activity to show.</p>
          <p>Start applying to jobs to see your activity here!</p>
        </div>
      )}
    </section>
  );
};

export default RecentActivity;