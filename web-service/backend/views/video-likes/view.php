<?php

use yii\helpers\Html;
use yii\widgets\DetailView;

/** @var yii\web\View $this */
/** @var app\models\VideoLikes $model */

$this->title = $model->LikeID;
$this->params['breadcrumbs'][] = ['label' => 'Video Likes', 'url' => ['index']];
$this->params['breadcrumbs'][] = $this->title;
\yii\web\YiiAsset::register($this);
?>
<div class="video-likes-view">

    <h1><?= Html::encode($this->title) ?></h1>

    <p>
        <?= Html::a('Update', ['update', 'LikeID' => $model->LikeID], ['class' => 'btn btn-primary']) ?>
        <?= Html::a('Delete', ['delete', 'LikeID' => $model->LikeID], [
            'class' => 'btn btn-danger',
            'data' => [
                'confirm' => 'Are you sure you want to delete this item?',
                'method' => 'post',
            ],
        ]) ?>
    </p>

    <?= DetailView::widget([
        'model' => $model,
        'attributes' => [
            'LikeID',
            'UserID',
            'VideoID',
            'LikedAt',
        ],
    ]) ?>

</div>
