def scmVars
node {
    stage('Checkout') {
        scmVars = checkout scm
        echo "Current branch: ${scmVars.GIT_BRANCH}"
    }
    // stage('Build') {
    //     if (scmVars.GIT_BRANCH.endsWith('/awake')) {
    //          sh 'dotnet restore --source https://api.nuget.org/v3/index.json --source https://nuget.awake-it.com'
    //          sh 'dotnet publish OperMate.Edge.DataFactory.WebApi/OperMate.Edge.DataFactory.WebApi.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Edge.DataFactory.WebApi/'
    //          sh 'dotnet publish OperMate.Edge.FakeAdapter.WebApi/OperMate.Edge.FakeAdapter.WebApi.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Edge.FakeAdapter.WebApi/'
    //          sh 'dotnet publish OperMate.Engine.JobController/OperMate.Engine.JobController.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Engine.JobController/'
    //          sh 'dotnet publish OperMate.Services.Authentication.WebApi/OperMate.Services.Authentication.WebApi.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Authentication.WebApi/'
    //          sh 'dotnet publish OperMate.Services.JobManagement.WebApi/OperMate.Services.JobManagement.WebApi.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.JobManagement/'
    //          sh 'dotnet publish OperMate.Services.Lobby.WebApi/OperMate.Services.Lobby.WebApi.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Lobby.WebApi/'
    //          sh 'dotnet publish OperMate.Services.Log.Web/OperMate.Services.Log.Web.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Log.Web'
    //          sh 'dotnet publish OperMate.Services.Mail.WebApi/OperMate.Services.Mail.WebApi.csproj -c Release -o /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Mail.WebApi/'
    //          sh 'rm -rf /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Presentations.Portal.Web && cp -R OperMate.Presentations.Portal.Web /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/'
    //     } else {
    //         echo "Skipped."
    //     }
    // }
    // stage('Build Image Docker') {
    //     if (scmVars.GIT_BRANCH.endsWith('/awake')) {
    //         sh 'docker build -t opermate.edge.datafactory.webapi -f OperMate.Edge.DataFactory.WebApi/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Edge.DataFactory.WebApi/'
    //         sh 'docker build -t opermate.edge.fakeadapter.webapi -f OperMate.Edge.FakeAdapter.WebApi/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Edge.FakeAdapter.WebApi/'
    //         sh 'docker build -t opermate.engine.jobcontroller -f OperMate.Engine.JobController/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Engine.JobController/'
    //         sh 'docker build -t opermate.services.authentication.webapi -f OperMate.Services.Authentication.WebApi/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Authentication.WebApi/'
    //         sh 'docker build -t opermate.services.jobmanagement.webapi -f OperMate.Services.JobManagement.WebApi/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.JobManagement/'
    //         sh 'docker build -t opermate.services.lobby.webapi -f OperMate.Services.Lobby.WebApi/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Lobby.WebApi/'
    //         sh 'docker build -t opermate.services.log.web -f OperMate.Services.Log.Web/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Log.Web/'
    //         sh 'docker build -t opermate.services.mail.webapi -f OperMate.Services.Mail.WebApi/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Services.Mail.WebApi/'
    //         sh 'docker build -t opermate.presentations.portal.web -f OperMate.Presentations.Portal.Web/Dockerfile /var/www/CARDX/BackEnd/DAT/data-workload-automation/OperMate/OperMate.Presentations.Portal.Web'
    //     } else {
    //         echo "Skipped."
    //     }
    // }
    stage('Deploy Docker') {
        if (scmVars.GIT_BRANCH.endsWith('/master')) {
            sh 'docker compose down'
            sh 'docker compose up -d --build'
        } else {
            echo "Skipped."
        }
    }
}