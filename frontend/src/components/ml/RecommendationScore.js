import React from 'react';
import './RecommendationScore.css';

const RecommendationScore = ({ score }) => {
  // Convert similarity score (usually 0-1) to percentage
  const percentage = Math.round((score || 