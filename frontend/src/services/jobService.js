import api from './api';

export const getJobs = async (params = {}) => {
  try {
    return await api.get('/jobs', { params });
  } catch (error) {
    throw error;
  }
};

export const getJobById = async (jobId) => {
  try {
    return await api.get(`/jobs/${jobId}`);
  } catch (error) {
    throw error;
  }
};

export const getRecommendedJobs = async (params = {}) => {
  try {
    return await api.get('/recommendations', { params });
  } catch (error) {
    throw error;
  }
};

export const applyForJob = async (jobId, applicationData) => {
  try {
    return await api.post(`/jobs/${jobId}/apply`, applicationData);
  } catch (error) {
    throw error;
  }
};
