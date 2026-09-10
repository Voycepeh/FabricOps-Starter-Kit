export const FPS = 30;
const seconds = [55, 65, 56, 65, 123, 39, 16];
const names = ['Introduction', 'Why FabricOps', 'Engineering choices', 'Connected workflow', 'Governance and Engineering', 'Promotion', 'Continue'];
export const OVERVIEW_SCENES = seconds.map((duration, index) => ({name:names[index], duration:duration*FPS, from:seconds.slice(0,index).reduce((sum,value)=>sum+value,0)*FPS}));
export const OVERVIEW_DURATION_IN_FRAMES = seconds.reduce((sum,value)=>sum+value,0)*FPS;
