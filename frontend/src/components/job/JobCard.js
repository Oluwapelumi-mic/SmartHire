import React from 'react';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import './JobCard.css';

const JobCard = ({ job }) => {
  const postedDate = new Date(job.created_at);
  const timeAgo = formatDistanceToNow(postedDate, { addSuffix: true });

  return (
    <div className="job-card">
      <div className="job-card-header">
        <h3 className="job-title">
          <Link to={`/jobs/${job.id}`}>{job.title}</Link>
        </h3>
        <div className="job-company">{job.company}</div>
        <div className="job-location">{job.location}</div>
      </div>
      
      <div className="job-card-body">
        <p className="job-description">
          {job.description.length > 150
            ? `${job.description.substring(0, 150)}...`
            : job.description}
        </p>
      </div>
      
      <div className="job-card-footer">
        <div className="job-skills">
          {job.skills.slice(0, 3).map((skill, index) => (
            <span key={index} className="skill-tag">
              {skill}
            </span>
          ))}
          {job.skills.length > 3 && (
            <span className="skill-tag more">+{job.skills.length - 3}</span>
          )}
        </div>
        
        <div className="job-meta">
          <span className="job-type">{job.job_type}</span>
          <span className="job-posted">Posted {timeAgo}</span>
        </div>
      </div>
    </div>
  );
};

export default JobCard;