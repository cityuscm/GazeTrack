import type { Session } from "$lib/structs";

export const apiRoutes = {
    client: () => fetch('/api/clients'),
    scene: () => fetch('/api/scenes'),
    status: () => fetch('/api/status'),
    session: (session: Session) => fetch('/api/session', {
        method: 'POST',
        body: JSON.stringify(session),
    }),
    control: (start: boolean) => fetch('/api/control', {
        method: 'POST',
        body: JSON.stringify({ start }),
    }),
}