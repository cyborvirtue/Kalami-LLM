<?php

/**
 * Coding by WangYuheng 2213040
 * 使用 Gii 生成了 Articles 的 CRUD
 * 参与数据库设计
 */

namespace app\models;

use yii\base\Model;
use yii\data\ActiveDataProvider;
use app\models\Articles;

/**
 * ArticlesSearch represents the model behind the search form of `app\models\Articles`.
 */
class ArticlesSearch extends Articles
{
    /**
     * {@inheritdoc}
     */
    public function rules()
    {
        return [
            [['ArticleID', 'AuthorID', 'ViewCount', 'LikeCount'], 'integer'],
            [['Title', 'Content', 'PublishedAt', 'UpdatedAt'], 'safe'],
        ];
    }

    /**
     * {@inheritdoc}
     */
    public function scenarios()
    {
        // bypass scenarios() implementation in the parent class
        return Model::scenarios();
    }

    /**
     * Creates data provider instance with search query applied
     *
     * @param array $params
     *
     * @return ActiveDataProvider
     */
    public function search($params)
    {
        $query = Articles::find();

        // add conditions that should always apply here

        $dataProvider = new ActiveDataProvider([
            'query' => $query,
        ]);

        $this->load($params);

        if (!$this->validate()) {
            // uncomment the following line if you do not want to return any records when validation fails
            // $query->where('0=1');
            return $dataProvider;
        }

        // grid filtering conditions
        $query->andFilterWhere([
            'ArticleID' => $this->ArticleID,
            'AuthorID' => $this->AuthorID,
            'PublishedAt' => $this->PublishedAt,
            'UpdatedAt' => $this->UpdatedAt,
            'ViewCount' => $this->ViewCount,
            'LikeCount' => $this->LikeCount,
        ]);

        $query->andFilterWhere(['like', 'Title', $this->Title])
            ->andFilterWhere(['like', 'Content', $this->Content]);

        return $dataProvider;
    }
}
