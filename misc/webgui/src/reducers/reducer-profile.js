/*
 * The users reducer will always return an array of users no matter what
 * You need to return something, so if there are no users then just return an empty array
 * */

export default function () {
    return [
        {
            id: 1,
            name: "Default",
            description: "Default dashboard view",
            thumbnail: "icons/awesome/chain.svg"
        },
        {
            id: 2,
            name: "Lights",
            description: "Show light devices",
            thumbnail: "icons/awesome/lightbulb-o.svg"
        },
        {
            id: 3,
            name: "Scenes",
            description: "Show configured scenes",
            thumbnail: "icons/weather/sunrise.svg"
        }
    ];
}
