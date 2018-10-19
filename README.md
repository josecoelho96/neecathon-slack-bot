# neecathon-slack-bot
A slack bot for the NEECathon!

## Deployment instructions
### Server side
1. Clone repository into server/machine: \
    `git clone <url>`
2. Change directory into the `deployment` directory: \
    `cd neeacthon-slack-bot/deployment`
3. Set `server_setup.sh` script as executable: \
    `chmod +x server_setup.sh`
4. Run script (might need sudo privileges): \
    `./server_setup.sh`
5. On the repository root (`neecathon-slack-bot`), run: \
    `python3 deployment/app_setup.py` \
This will create the env file and create all channels/groups needed.
6. Execute the command: \
    `docker-compose up -d`
7. The docker-compose should be running and a message should have been posted on the logs channel. If not, please check the logs to detect the errors.
8. Do one (any) request with the admin account. It will fail, but don't worry.
9. On the terminal, type: \
    `docker exec -ti <database-container-name> psql --username=<db-user-name> <db-name>` \
    Eg: `docker exec -ti neecathon-db psql --username=neecathon-bot-db-user neecathon-bot-db`

10. Now type the following on the `psql` prompt: \
    `\c database_name` (Example: `\c neecathon-bot-db`)
11. Type: \
    ` SELECT * FROM users;` which should give you one row with the user id of the admin account.
12. Type: \
    ` INSERT INTO permissions(user_id, staff_function) VALUES ('<user-id>', 'admin');`
13. The user should now be an admin.

### Slack side
1. Create new user, and setup the profile (full name, display name, user details, user photo). This user will be used to generate the token and must have full access to the repository.
2. Change settings of the workspace:
    1. **Workspace Signup Mode:** *Invitation only*
    2. **Workspace Icon:** *If desired*
    3. **Permissions: -> Invitations:** *Disable 'Allow everyone (except guests) to invite new members. '*
    4. **Permissions: -> Channel Management:** *Change all options to 'Workspace Owners' only.*
3. Create new application:
    1. Setup *App Name*, *Short Description* and *App Icon*.
    2. On *OAuth & Permissions*, add the required scopes:
        1. Modify your public channels -  channels:write
        2. Send messages as NEECathon App - chat:write:bot
        3. Modify your private channels -  groups:write
    3. On the same tab, publish the application and save the OAuth Access Token on the .env file.
4. Add all slash commands. Never forget to enable 'Escape Names'.

## Commands Syntax (Portuguese description)
Command | Description
--------|--------
`/saldo` | *Consulta o teu saldo.*
`/criar-equipa nome-equipa` | *Cria uma nova equipa.*
`/entrar código-equipa` | *Entra numa equipa.*
`/compra @destinatario quantia descrição` | *Realiza uma compra.*
`/movimentos [quantidade]` | *Vê os últimos movimentos da tua equipa.*
`/ver-equipas` | *Vê a lista das equipas em competição.*
`/ver-equipas-registo` | *Vê os códigos de registo das várias equipas.*
`/detalhes @user\|user-id` | *Mostra os detalhes de um utilizador.*
`/meus-movimentos [quantidade]` | *Vê os teus últimos movimentos.*
`/alterar-permissoes @user admin\|staff\|remover` | *Altera as permissões de um utilizador.*
`/ver-staff` | *Vê a lista de elementos da staff.*
`/hackerboy quantia descrição` | *Rouba ou dá dinheiro a todos.*
`/hackerboy-equipa id-equipa quantia descrição` | *Dá ou tira dinheiro a uma equipa.*
`/transacoes-participante @user [quantidade]` | *Mostra as transações de um participante.*
`/transacoes-equipa id-equipa [quantidade]` | *Vê os últimos movimentos de uma equipa.*
`/transacoes-todas [quantidade]` | *Vê os últimos movimentos.*
`/detalhes-equipa id-equipa` | *Vê os detalhes de uma equipa.*

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
### List last user transactions
`/meus-movimentos <qty>`
List user transactions. If the user has a team, list his last `qty` transactions. If the current user doesn't have a team, an error message appears stating how to join a team.
### Change user role/add to staff
`/alterar-permissoes <@user> <admin|staff|remover>`
Changes the permissions of `user`, adding it to the staff crew if it wasn't on it yet. If the `remover` option is selected, the user is removed from the staff team.
### List staff elements
`/ver-staff`
List all elements in staff, along with their role and their ID. Only accessible to staff elements.
### Hackerboy
`/hackerboy <money-change> <description>`
Can only be performed by admins. Used to change all teams balances, either to give them money or to remove it.
### Team Hackerboy
`/hackerboy-equipa <team-id> <money-change> <description>`
Can only be performed by admins. Used to change a team balance, either to give it money or to remove it.
### List given user transactions
`/transacoes-participante @user <qty>`
Lists the last `qty` transactions made/received by `@user`
### List given team transactions
`/transacoes-equipa <team-id> <qty>`
Lists the last `qty` transactions made/received by users in team with id `team-id`
### List all transactions
`/transacoes-todas <qty>`
Lists the last `qty` transactions made/received in the entire application.

## Current features:
- Request origin verification/validation
- Roles/Permissions
- Auto add users to channels
- Report money receival on buy operation
- Report logs to channel

## Commands to add
- TBD

## Features to add
- Add/remove staff from staff channel

## Problems found
- How to create first admin.
- FIXED: ~~Implementation: Log levels aren't well defined.~~
- FIXED: ~~Entry codes are not being verified as unique. Not using UUID.~~
- FIXED: ~~Users are only added to users table on join team commands, should be done always, but on every request will make this slow.~~

## Bug list
- ...

## Small fixes
- TBA
