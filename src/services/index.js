import api, { fileService, projectService } from './api';
import videoService from './videoService';
import projectServiceModule from './projectService';

// Exportar todos os serviços
export {
  api as default,
  fileService,
  projectService,
  videoService,
  projectServiceModule as projectServiceExtended,
};
