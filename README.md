# neecathon-slack-bot
A slack bot for the NEECathon!

## Valid commands
### Create team
`/criar-equipa [team name]`
Creates a new team, if the name doesn't exists already.  Returns the newly created team information: The name, ID and a access key, which allows users to enter the team using that code. Reports an error stating that a team cannot be created if something fails. If the team name already exists the team isn't created and an error message appears in the chat.
### Join team
`/entrar [entry-code]`
Joins the team with the defined `entry-code`, if exists. If the `entry-code` is valid, the user receives a message and joins the team. If it's invalid, an error message pops up.
### Balance check
`/saldo`
Shows the team-wise current balance. If the user does not have a team, an error message appears stating how to join a team.
### Buy
`/compra [@destination_user] [qty] [description]`
Allows to buy something from another user. It performs a transfer, between the command caller and the `destination_user`, by giving him `qty` credits. A short description must be provided to describe the transaction. If `destination_user` isn't enrolled in a team, an error message will be displayed stating that. If `qty` is invalid (unparsable, negative, null or above team actual balance), the user will get an error message explaining the problem.
### List last transactions
`/movimentos <qty>`
List transactions. If the user has a team, list the last `qty` transactions of his team. If the current user doesn't have a team, an error message appears stating how to join a team.
### List all teams
`/ver-equipas`
List all teams. Provides the team name and team id of each team participating.
### List all teams registered
`/ver-equipas-registo`
List all registered teams. Provides the team name and team id and entry code of each team registered.
### View team details
`/detalhes-equipa <team_id>`
Used to list all details of a team. The `team-id` must be provided.
### View user details
`/detalhes-participante <@user|user-id>`
Used to list details of a participant. The `@user` or `user-id` must be provided.

## Current features:
- Request origin verification/validation
- Roles/Permissions

## To be added
```./bug <money-change> <description>``` \
Can only be performed by admins. Used to change all teams balances.

```./tornar-admin <@user>``` \
Can only be performed by admins. Used to make `@user` an admin.

## Features to add
- Auto add users to channels
- Report logs to channel
- Report money receival on buy operation
- Error codes
- Single user transactions listing

## Problems found
- How to create first admin.
- Implementation: Log levels aren't well defined.
- IDs are not being verified as unique.

## Bug list
- ...

## Small fixes
- TBA