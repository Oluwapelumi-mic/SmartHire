import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { getRecommendedJobs } from '../../services/jobService';
import { getUserApplications } from '../../services/applicationService';
import { getProfile } from '../../services/profileService';
import JobCard from '../job/JobCard';
import RecommendationScore from '../ml/RecommendationScore';
import ProfileCompleteness from './ProfileCompleteness';
import RecentActivity from './RecentActivity';
import './DashboardOverview.css';

const DashboardOverview = () => {
  const { currentUser } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [applications, setApplications] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch data in parallel
        const [recommendationsData, applicationsData, profileData] = await Promise.all([
          getRecommendedJobs({ limit: 3 }),
          getUserApplications(),
          getProfile()
        ]);
        
        setRecommendations(recommendationsData.recommendations || []);
        setApplications(applicationsData.applications || []);
        setProfile(profileData.profile);
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading your personalized dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h3>Oops! Something went wrong</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    );
  }

  // Calculate profile completeness
  const calculateProfileCompleteness = () => {
    if (!profile) return 0;
    
    const requiredFields = [
      'headline', 
      'summary', 
      'job_title', 
      'location', 
      'experience_years',
      'education',
      'desired_job_type'
    ];
    
    const filledFields = requiredFields.filter(field => 
      profile[field] && profile[field].trim !== ''
    );
    
    // Skills and experiences add more weight
    let score = (filledFields.length / requiredFields.length) * 70;
    
    if (profile.skills && profile.skills.length > 0) {
      score += Math.min(profile.skills.length * 2, 15);
    }
    
    if (profile.experiences && profile.experiences.length > 0) {
      score += Math.min(profile.experiences.length * 5, 15);
    }
    
    return Math.min(Math.round(score), 100);
  };

  const profileScore = calculateProfileCompleteness();

  return (
    <div className="dashboard-overview">
      <div className="dashboard-welcome">
        <h1>Welcome back, {currentUser.first_name}!</h1>
        <p className="welcome-message">
          Here's your personalized job search summary
        </p>
      </div>
      
      <div className="dashboard-grid">
        <div className="dashboard-main">
          {/* Job Recommendations */}
          <section className="dashboard-section recommendations-section">
            <div className="section-header">
              <h2>Recommended Jobs For You</h2>
              <a href="/jobs" className="view-all-link">View All Jobs</a>
            </div>
            
            {recommendations.length > 0 ? (
              <div className="recommendations-list">
                {recommendations.map((job) => (
                  <div key={job.id} className="recommendation-item">
                    <JobCard job={job} />
                    <RecommendationScore score={job.similarity_score} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>
                  We need more information about your skills and experience to provide
                  personalized recommendations.
                </p>
                <a href="/profile" className="action-button">
                  Complete Your Profile
                </a>
              </div>
            )}
          </section>
          
          {/* Recent Applications */}
          <section className="dashboard-section applications-section">
            <div className="section-header">
              <h2>Your Recent Applications</h2>
              <a href="/applications" className="view-all-link">View All Applications</a>
            </div>
            
            {applications.length > 0 ? (
              <div className="applications-list">
                {applications.slice(0, 3).map((application) => (
                  <div key={application.id} className="application-item">
                    <div className="application-company">
                      <h3>{application.job.company}</h3>
                      <span className={`status-badge ${application.status}`}>
                        {application.status}
                      </span>
                    </div>
                    <h4>{application.job.title}</h4>
                    <p className="application-date">
                      Applied on {new Date(application.applied_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>You haven't applied to any jobs yet.</p>
                <a href="/jobs" className="action-button">
                  Explore Jobs
                </a>
              </div>
            )}
          </section>
        </div>
        
        <div className="dashboard-sidebar">
          {/* Profile Completeness */}
          <ProfileCompleteness 
            score={profileScore} 
            profile={profile} 
          />
          
          {/* Recent Activity */}
          <RecentActivity 
            applications={applications} 
          />
          
          {/* Career Tips */}
          <section className="dashboard-section tips-section">
            <h3>Career Tips</h3>
            <div className="tip-card">
              <h4>Optimize Your Resume</h4>
              <p>Use keywords from job descriptions to match your skills with what employers are looking for.</p>
            </div>
            <div className="tip-card">
              <h4>Prepare for Interviews</h4>
              <p>Research the company and prepare specific examples that demonstrate your skills.</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;