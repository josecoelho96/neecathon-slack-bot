# neecathon-slack-bot
A slack bot for the NEECathon!

## Valid commands:
```./criar-equipa [team name]``` - Creates a new team, if the name doesn't exists already.\
Returns the team ID, a key to later join the team and the team name.


```./entrar [team-code]``` - Joins the team with the defined code, if exists.\
TODO: Join the user to channels.


```./saldo``` - Shows the current balance (team-wise).


```./compra [@user] [qtd] [description]``` - Allows to buy something from another user.
TODO: Posts a message to channels.


```./movimentos <qtd>``` - List transactions. \
This command can be used by either users and admins. \
If the user has a team, list the last `qtd` transactions of his team. \
**TODO:** \
If performed by an admin, list the last `qtd` transactions of all teams. \
An admin can add the `team-id` as a argument to view the transactions of only one team.


## To be added



```./ver-equipas``` - List all teams. \
Can only be performed by admins. Used to list all teams.


```./detalhes-equipa <team>``` \
Can only be performed by admins. Used to list all details of a team. The `team-id` must be provided.


```./bug <money-change> <description>``` \
Can only be performed by admins. Used to change all teams balances.


```./adicionar-informacao <nome|email> <value>``` \
Can be performed by users, to add some personal information on his account (name and email). \
An admin can also use this command on other user, by providing the `@user` has a first argument.

```./informacoes``` \
If performed by an user/admin, returns all informations related to his account. \
An admin can also use this command to retrieve all information on some user by providing the `@user`.


```./tornar-admin <@user>``` \
Can only be performed by admins. Used to make `@user` an admin.




## Features to add
- Verify requests origin and validation
- Auto add users to channels
- Report logs to channel
- Report money receival on buy operation
- Permissions system

## Problems found
- How to create first admin.

## Bug list
- ...