export interface ServerConnection {
    ip: string;
    port: number;
}

export interface Session {
    clients: string[];
    scene: string;
}