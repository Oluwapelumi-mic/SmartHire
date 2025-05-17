import React, { useMemo } from 'react';
import './SkillMatchIndicator.css';

const SkillMatchIndicator = ({ userSkills, jobSkills, matchScore }) => {
  const matchedSkills = useMemo(() => {
    if (!userSkills || !jobSkills) return [];
    return userSkills.filter(skill => 
      jobSkills.some(jobSkill => 
        jobSkill.toLowerCase() === skill.toLowerCase()
      )
    );
  }, [userSkills, jobSkills]);

  const missingSkills = useMemo(() => {
    if (!userSkills || !jobSkills) return [];
    return jobSkills.filter(skill => 
      !userSkills.some(userSkill => 
        userSkill.toLowerCase() === skill.toLowerCase()
      )
    );
  }, [userSkills, jobSkills]);

  // Use provided match score or calculate a basic percentage
  const score = matchScore || (jobSkills.length > 0 
    ? Math.round((matchedSkills.length / jobSkills.length) * 100) 
    : 0);
  
  const getMatchClass = () => {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'moderate';
    return 'low';
  };

  return (
    <div className="skill-match-indicator">
      <div className="match-score">
        <div className={`score-circle ${getMatchClass()}`}>
          <span className="score-value">{score}%</span>
        </div>
        <span className="match-label">Match</span>
      </div>
      
      <div className="skills-breakdown">
        {matchedSkills.length > 0 && (
          <div className="matched-skills">
            <h4>Your Matching Skills</h4>
            <ul>
              {matchedSkills.map((skill, index) => (
                <li key={index} className="matched">{skill}</li>
              ))}
            </ul>
          </div>
        )}
        
        {missingSkills.length > 0 && (
          <div className="missing-skills">
            <h4>Skills to Develop</h4>
            <ul>
              {missingSkills.map((skill, index) => (
                <li key={index} className="missing">{skill}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default SkillMatchIndicator;